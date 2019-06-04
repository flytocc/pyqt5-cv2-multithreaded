from PyQt5.QtCore import QRect


class ImageProcessingSettings(object):
    def __init__(self):
        self.smoothType = int()
        self.smoothParam1 = int()
        self.smoothParam2 = int()
        self.smoothParam3 = float()
        self.smoothParam4 = float()
        self.dilateNumberOfIterations = int()
        self.erodeUrlOfIterations = int()
        self.flipCode = int()
        self.cannyThreshold1 = float()
        self.cannyThreshold2 = float()
        self.cannyApertureSize = int()
        self.cannyL2gradient = bool()


class ImageProcessingFlags(object):
    def __init__(self):
        self.grayscaleOn = False
        self.smoothOn = False
        self.dilateOn = False
        self.erodeOn = False
        self.flipOn = False
        self.cannyOn = False


class MouseData(object):
    def __init__(self):
        self.selectionBox = QRect()
        self.leftButtonRelease = bool()
        self.rightButtonRelease = bool()


class ThreadStatisticsData(object):
    def __init__(self):
        self.averageFPS = 0.0
        self.nFramesProcessed = 0
