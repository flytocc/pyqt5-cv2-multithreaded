from PyQt5.QtCore import QThread

# Version information
APP_VERSION = '2.3.3-Python'

# SQL
DEFAULT_SQL_HOST = '121.42.233.94'
DEFAULT_SQL_PORT = 3306
DEFAULT_SQL_USER = 'root'
DEFAULT_SQL_PASSWORD = '56731421'
DEFAULT_SQL_DataBase = 'heatmap'

DEFAULT_BOXES_BUFFER = 5
DEFAULT_UPLOAD_ELAPSED_TIME = 200

# Rtsp transport mode
DEFAULT_TRANSPORT_MODE = 0  # 0 -> none, 1 -> unicast, 2 -> multicast
# Url mode
DEFAULT_URL_MODE = 'filename'  # 'device url', 'rtsp', 'filename'
# Filename
DEFAULT_FILENAME = 'C:/Users/Lenny/Videos/final.mp4'
# Device url
DEFAULT_DEVICE_URL = 'rtsp://admin:caffe2018@192.168.11.101:554/Streaming/Channels/102'
DEFAULT_RTSP_USER = 'admin'
DEFAULT_RTSP_PASSWORD = 'caffe2018'
DEFAULT_RTSP_IP = '192.168.11.100'
DEFAULT_RTSP_PORT = '554'
DEFAULT_RTSP_CAHHELS = '102'

# FPS statistics queue lengths
PROCESSING_FPS_STAT_QUEUE_LENGTH = 32
CAPTURE_FPS_STAT_QUEUE_LENGTH = 32

# Image buffer size
DEFAULT_IMAGE_BUFFER_SIZE = 2
# Drop frame if image/frame buffer is full
DEFAULT_DROP_FRAMES = True
# ApiPreference for OpenCv.VideoCapture
DEFAULT_APIPREFERENCE = 'CAP_ANY'
# Thread priorities
DEFAULT_CAP_THREAD_PRIO = QThread.NormalPriority
DEFAULT_PROC_THREAD_PRIO = QThread.HighestPriority
DEFAULT_SQL_THREAD_PRIO = QThread.HighPriority

# IMAGE PROCESSING
# Smooth
DEFAULT_SMOOTH_TYPE = 0  # Options: [BLUR=0,GAUSSIAN=1,MEDIAN=2]
DEFAULT_SMOOTH_PARAM_1 = 3
DEFAULT_SMOOTH_PARAM_2 = 3
DEFAULT_SMOOTH_PARAM_3 = 0
DEFAULT_SMOOTH_PARAM_4 = 0
# Dilate
DEFAULT_DILATE_ITERATIONS = 1
# Erode
DEFAULT_ERODE_ITERATIONS = 1
# Flip
DEFAULT_FLIP_CODE = 1  # Options: [x-axis=0,y-axis=1,both axes=-1]
# Canny
DEFAULT_CANNY_THRESHOLD_1 = 10
DEFAULT_CANNY_THRESHOLD_2 = 00
DEFAULT_CANNY_APERTURE_SIZE = 3
DEFAULT_CANNY_L2GRADIENT = False

# Cap url for push button
CAP_URL = ['/root/testvideo/192.168.11.101_01_2019042515373473.mp4',
           '/root/testvideo/192.168.11.102_01_20190425153738487.mp4',
           '/root/testvideo/192.168.11.103_01_20190425153741889.mp4',
           '/root/testvideo/192.168.11.104_01_20190425153745810.mp4',
           '/root/testvideo/192.168.11.105_01_20190425153750343.mp4',
           '/root/testvideo/192.168.11.106_01_20190425153754209.mp4']
