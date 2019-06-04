from PyQt5.QtCore import QThread

# Version information
APP_VERSION = '2.3.3-Python'

# Url mode
DEFAULT_URL_MODE = 'device url'  # 'device url', 'rtsp', 'filename'
# Filename
DEFAULT_FILENAME = ''
# Device url
DEFAULT_DEVICE_URL = 'rtsp://'
DEFAULT_RTSP_USER = ''
DEFAULT_RTSP_PASSWORD = ''
DEFAULT_RTSP_IP = ''
DEFAULT_RTSP_PORT = ''
DEFAULT_RTSP_CAHHELS = ''

# Rtsp transport mode
DEFAULT_TRANSPORT_MODE = 0  # 0 -> none, 1 -> unicast, 2 -> multicast

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
