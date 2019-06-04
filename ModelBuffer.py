from PyQt5.QtCore import QMutexLocker, QMutex, QWaitCondition, QSemaphore
import os
import time
import numpy as np
import pprint
from tqdm import tqdm

import torch
import torch.backends.cudnn as cudnn
from torch.autograd import Variable

from pet.utils.misc import AverageMeter, weight_filler
from pet.ssd.core.config import cfg, merge_cfg_from_file

os.environ['CUDA_VISIBLE_DEVICES'] = cfg.GPU_IDS

from pet.ssd.modeling.model_builder import Generalized_SSD
from pet.ssd.datasets.data_augment import BaseTransform
from pet.ssd.ops.functions import Detect, PriorBox
import pet.ssd.utils.vis as vis_utils
import pet.maskrcnn.utils.boxes as box_utils


def get_weights(mode='latest'):
    if os.path.exists(cfg.TEST.WEIGHTS):
        weights = cfg.TEST.WEIGHTS
    else:
        weights = os.path.join(cfg.CKPT, 'model_{}.pth'.format(mode))
    return weights


class ModelBuffer(object):
    def __init__(self, modelNumPerGpu=1, cfg_file='./cfgs/ssd/persondetect/ssd_VGG16_512x512_1x_real.yaml',
                 dynamicAllocation=True):
        # Initialize variables(s)
        self.nArrived = 0
        self.doSync = False
        self.syncSet = set()
        self.soleGpuIdMutex = QMutex()

        self.dynamicAllocation = dynamicAllocation
        self.modelNumPerGpu = modelNumPerGpu
        self.wc = QWaitCondition()
        self.mutex = QMutex()
        self.freeSlots = QSemaphore(len(cfg.GPU_IDS.split(',')) * modelNumPerGpu - (1 if dynamicAllocation else 0))
        self.usedSlots = QSemaphore(0)

        # For sole gpu
        self.soleGpuFreeSlots = QSemaphore(1)
        self.soleGpuUsedSlots = QSemaphore(0)
        self.soleGpuFreeSlots.acquire()
        self.soleGpuUsedSlots.release()



        cudnn.benchmark = True
        if cfg_file is not None:
            merge_cfg_from_file(cfg_file)
        cfg.USE_GPU = True

        print("Using config:")
        pprint.pprint(cfg)

        self.freeGpus = {}
        self.keyGpuIdMap = {}
        self.modelDict = {}
        self.deviceDict = {}
        self.priorsDict = {}
        self.detectorDict = {}

        for gpu_id in tqdm(cfg.GPU_IDS.split(',')):
            for i in range(modelNumPerGpu):
                self.add(int(gpu_id), i)


        self.soleGpuId = 'gpu%s_%d' % (cfg.GPU_IDS.split(',')[-1], 0) if dynamicAllocation else ''


    def add(self, gpu_id, idx):
        cur_dev = torch.cuda.current_device()
        torch.cuda.set_device(gpu_id)
        dev = torch.device("cuda:%d" % gpu_id)
        model = Generalized_SSD()

        # Load trained model
        target_model = get_weights()
        pretrained_dict = torch.load(target_model)
        model_dict = model.state_dict()
        updated_dict, match_layers, mismatch_layers = weight_filler(pretrained_dict, model_dict)
        model_dict.update(updated_dict)
        model.load_state_dict(model_dict)

        detector = Detect(cfg.MODEL.NUM_CLASSES, 0, cfg.DATASET[cfg.DATASET.PRIORBOX_TYPE].VARIANCE)
        priorbox = PriorBox(cfg.DATASET[cfg.DATASET.PRIORBOX_TYPE])  # e.g., DATASET.VOC300
        priors = Variable(priorbox.forward())

        # Define loss function (criterion) and optimizer
        model.cuda()
        if cfg.MODEL.HALF_PRECISION:
            model = model.half()
            priors = priors.half()

        # switch to train mode
        model.eval()

        key = 'gpu%d_%d' % (gpu_id, idx)
        self.deviceDict[key] = dev
        self.modelDict[key] = model
        self.priorsDict[key] = priors
        self.detectorDict[key] = detector
        self.keyGpuIdMap[key] = gpu_id

        ret = self.freeSlots.tryAcquire()
        with QMutexLocker(self.mutex):
            self.freeGpus[key] = ret
        if ret:
            self.usedSlots.release()

        torch.cuda.set_device(cur_dev)

    def getFreeGpuByGpuId(self):
        with QMutexLocker(self.mutex):
            for k, v in self.freeGpus.items():
                if v:
                    self.freeGpus[k] = False
                    return k

    def detection(self, img, first):
        if not first:
            self.usedSlots.acquire()
            key = self.getFreeGpuByGpuId()
            self.freeSlots.release()
        else:
            self.soleGpuUsedSlots.acquire()
            key = self.soleGpuId
            self.soleGpuFreeSlots.release()

        batch_time = AverageMeter()
        data_time = AverageMeter()
        detect_time = AverageMeter()
        postproc_time = AverageMeter()
        tic = time.time()

        torch.cuda.set_device(self.keyGpuIdMap[key])
        x = BaseTransform(cfg.MODEL.IMAGE_SIZE[0], cfg.PIXEL_MEANS, cfg.PIXEL_STDS, (2, 0, 1))(img).unsqueeze(0)
        if cfg.USE_GPU:
            x = x.cuda()
        if cfg.MODEL.HALF_PRECISION:
            x = x.half()

        # measure data loading time
        data_time.update(time.time() - tic)
        tmp_tic = time.time()

        out = self.modelDict[key](x=x, is_training=False)  # forward pass
        boxes, scores = self.detectorDict[key].forward(out, self.priorsDict[key])

        detect_time.update(time.time() - tmp_tic)
        tmp_tic = time.time()

        boxes = boxes[0]
        scores = scores[0]

        boxes = boxes.cpu().numpy()
        scores = scores.cpu().numpy()
        # scale each detection back up to the image
        scale = torch.Tensor([img.shape[1], img.shape[0], img.shape[1], img.shape[0]]).cpu().numpy()
        boxes *= scale

        all_boxes = [[[]] for _ in range(cfg.MODEL.NUM_CLASSES)]
        cls_boxes_i = [[] for _ in range(cfg.MODEL.NUM_CLASSES)]  # for vis
        for j in range(1, cfg.MODEL.NUM_CLASSES):
            inds = np.where(scores[:, j] > cfg.TEST.SCORE_THRESH)[0]
            if len(inds) == 0:
                all_boxes[j][0] = np.empty([0, 5], dtype=np.float32)
                continue
            boxes_j = boxes[inds]
            boxes_j = box_utils.clip_tiled_boxes(boxes_j, img.shape)
            scores_j = scores[inds, j]
            dets_j = np.hstack((boxes_j, scores_j[:, np.newaxis])).astype(np.float32, copy=False)

            if cfg.TEST.SOFT_NMS.ENABLED:
                nms_dets, _ = box_utils.soft_nms(
                    dets_j,
                    sigma=cfg.TEST.SOFT_NMS.SIGMA,
                    overlap_thresh=cfg.TEST.NMS,
                    score_thresh=0.0001,
                    method=cfg.TEST.SOFT_NMS.METHOD
                )
            else:
                keep = box_utils.nms(dets_j, cfg.TEST.NMS)
                nms_dets = dets_j[keep, :]
            # Refine the post-NMS boxes using bounding-box voting
            if cfg.TEST.BBOX_VOTE.ENABLED:
                nms_dets = box_utils.box_voting(
                    nms_dets,
                    dets_j,
                    cfg.TEST.BBOX_VOTE.VOTE_TH,
                    scoring_method=cfg.TEST.BBOX_VOTE.SCORING_METHOD
                )

            all_boxes[j][0] = nms_dets
            cls_boxes_i[j] = nms_dets

        # if cfg.VIS.ENABLED:
        vis_im = vis_utils.vis_one_image_opencv(img, cls_boxes_i)

        if cfg.TEST.DETECTIONS_PER_IM > 0:
            image_scores = np.hstack([all_boxes[j][0][:, -1] for j in range(1, cfg.MODEL.NUM_CLASSES)])
            if len(image_scores) > cfg.TEST.DETECTIONS_PER_IM:
                image_thresh = np.sort(image_scores)[-cfg.TEST.DETECTIONS_PER_IM]
                for j in range(1, cfg.MODEL.NUM_CLASSES):
                    keep = np.where(all_boxes[j][0][:, -1] >= image_thresh)[0]
                    all_boxes[j][0] = all_boxes[j][0][keep, :]

        postproc_time.update(time.time() - tmp_tic)
        # measure elapsed time
        batch_time.update(time.time() - tic)
        tic = time.time()

        # print('Testing: Best_MAP: {:4.4f} | Time: {:.3f} | Data: {:.3f} | Det: {:.3f} | '
        #       'Post: {:.3f} | LR: {:.8f} | Total: {:.3f}'
        #       .format(cfg.STATE.BEST_MAP,
        #               batch_time.average(),
        #               data_time.average(),
        #               detect_time.average(),
        #               postproc_time.average(),
        #               cfg.STATE.CUR_LR, batch_time.sum))
        if not first:
            self.freeSlots.acquire()
            with QMutexLocker(self.mutex):
                self.freeGpus[key] = True
            self.usedSlots.release()
        else:
            self.soleGpuFreeSlots.acquire()
            self.soleGpuUsedSlots.release()

        return vis_im, cls_boxes_i

    def wakeAll(self):
        with QMutexLocker(self.mutex):
            self.wc.wakeAll()
