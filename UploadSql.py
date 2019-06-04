from PyQt5.QtCore import QThread, QMutexLocker, QMutex, QWaitCondition, QTime, qDebug
from queue import Queue
import time
import pymysql
import numpy as np

from Config import *


class SharedBoxesBuffer(QThread):
    def __init__(self, parent=None):
        super(SharedBoxesBuffer, self).__init__(parent)
        # Initialize variables(s)
        self.nArrived = [False for _ in range(6)]
        self.boxesBufferDict = dict()
        self.cameraIdDict = dict()

        # Save Device Url
        self.boxesBufferMax = DEFAULT_BOXES_BUFFER
        self.boxesBuffer = self.boxesBufferMax
        self.upload_elapsed_time = DEFAULT_UPLOAD_ELAPSED_TIME
        self.uploadingMutex = QMutex()
        self.doStopMutex = QMutex()
        self.t = QTime()
        self.processingTime = 0
        self.doStop = False
        self.sampleNumber = 0
        self.fpsSum = 0.0
        self.fps = Queue()
        self.averageFPS = 0
        self.vis_th = 0.7

        self.connect = pymysql.Connect(DEFAULT_SQL_HOST,
                                       DEFAULT_SQL_USER,
                                       DEFAULT_SQL_PASSWORD,
                                       DEFAULT_SQL_DataBase,
                                       DEFAULT_SQL_PORT)
        self.cursor = self.connect.cursor()

        self.finished.connect(self.closeSql)

    def run(self):
        while True:
            ##############################
            # Stop thread if doStop=True #
            ##############################
            self.doStopMutex.lock()
            if self.doStop:
                self.doStop = False
                self.doStopMutex.unlock()
                break
            self.doStopMutex.unlock()
            ################################
            ################################

            with QMutexLocker(self.uploadingMutex):
                ##################################
                # PERFORM IMAGE PROCESSING BELOW #
                ##################################

                if all(self.nArrived) and len(self.boxesBufferDict) == 6:
                    data = ['' for _ in range(6)]
                    timestamp_10ms = time.time() * 10
                    for deviceUrl, cls_boxes in self.boxesBufferDict.items():
                        cameraId = self.cameraIdDict[deviceUrl]
                        box_list = [b for b in cls_boxes if len(b) > 0]
                        if len(box_list) > 0:
                            boxes = np.concatenate(box_list)
                            bbox = boxes[:, :5]
                            if max(boxes[:, 4]) >= self.vis_th:
                                data[cameraId] = ','.join(['%d,%d,%d,%d' % (x, y, h, w) for x, y, h, w, s in bbox if s > self.vis_th])
                            else:
                                data[cameraId] = ''
                        else:
                            data[cameraId] = ''
                    sql = "INSERT INTO trade (stamp, data1, data2, data3, data4, data5, data6) " \
                          "VALUES ('%.0f', '%s', '%s', '%s', '%s', '%s', '%s')"
                    self.cursor.execute(sql % (timestamp_10ms, data[0], data[1], data[2], data[3], data[4], data[5]))
                    self.boxesBuffer -= 1
                    if self.boxesBuffer == 0:
                        self.boxesBuffer = self.boxesBufferMax
                        self.connect.commit()
                        print("Upload sql data %.0f", timestamp_10ms)

                    self.nArrived = [False for _ in range(6)]

                ##################################
                # PERFORM IMAGE PROCESSING ABOVE #
                ##################################

            self.processingTime = self.t.elapsed()
            delta = DEFAULT_UPLOAD_ELAPSED_TIME - self.t.elapsed()
            if delta > 0:
                self.msleep(delta)
            # Save processing time
            self.processingTime = self.t.elapsed()
            self.updateFPS(self.processingTime)
            # Start timer (used to calculate processing rate)
            self.t.start()

        qDebug("Stopping upload sql thread...")

    def closeSql(self):
        self.cursor.close()
        self.connect.close()

    def stop(self):
        with QMutexLocker(self.doStopMutex):
            self.doStop = True

    def add(self, deviceUrl, boxes):
        # Add image buffer to map
        with QMutexLocker(self.uploadingMutex):
            self.boxesBufferDict[deviceUrl] = boxes
            if self.cameraIdDict.get(deviceUrl) is None:
                self.cameraIdDict[deviceUrl] = len(self.cameraIdDict)
            cameraId = self.cameraIdDict[deviceUrl]
            self.nArrived[cameraId] = True

    def updateFPS(self, timeElapsed):
        # Add instantaneous FPS value to queue
        if timeElapsed > 0:
            self.fps.put(1000 / timeElapsed)
            # Increment sample number
            self.sampleNumber += 1

        # Maximum size of queue is DEFAULT_PROCESSING_FPS_STAT_QUEUE_LENGTH
        if self.fps.qsize() > PROCESSING_FPS_STAT_QUEUE_LENGTH:
            self.fps.get()

        # Update FPS value every DEFAULT_PROCESSING_FPS_STAT_QUEUE_LENGTH samples
        if self.fps.qsize() == PROCESSING_FPS_STAT_QUEUE_LENGTH and self.sampleNumber == PROCESSING_FPS_STAT_QUEUE_LENGTH:
            # Empty queue and store sum
            while not self.fps.empty():
                self.fpsSum += self.fps.get()
            # Calculate average FPS
            self.averageFPS = self.fpsSum / PROCESSING_FPS_STAT_QUEUE_LENGTH
            # Reset sum
            self.fpsSum = 0.0
            # Reset sample number
            self.sampleNumber = 0
