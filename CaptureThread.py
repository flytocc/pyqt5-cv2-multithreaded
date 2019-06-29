from PyQt5.QtCore import QThread, QTime, QMutexLocker, QMutex, pyqtSignal, qDebug
from PyQt5.QtWidgets import QMessageBox
import cv2
from queue import Queue
import os

from Structures import *
from Config import *


class CaptureThread(QThread):
    updateStatisticsInGUI = pyqtSignal(ThreadStatisticsData)
    end = pyqtSignal()

    def __init__(self, sharedImageBuffer, deviceUrl, dropFrameIfBufferFull, apiPreference, width, height, parent=None):
        super(CaptureThread, self).__init__(parent)
        self.cap = cv2.VideoCapture()
        self.t = QTime()
        self.doStopMutex = QMutex()
        self.fps = Queue()
        # Save passed parameters
        self.sharedImageBuffer = sharedImageBuffer
        self.dropFrameIfBufferFull = dropFrameIfBufferFull
        self.deviceUrl = deviceUrl
        self._deviceUrl = int(deviceUrl) if deviceUrl.isdigit() else deviceUrl
        self.localVideo = True if os.path.exists(self._deviceUrl) else False
        self.apiPreference = apiPreference
        self.width = width
        self.height = height
        # Initialize variables(s)
        self.captureTime = 0
        self.doStop = False
        self.sampleNumber = 0
        self.fpsSum = 0.0
        self.statsData = ThreadStatisticsData()
        self.defaultTime = 0

    def run(self):
        pause = False
        while True:
            ################################
            # Stop thread if doStop = TRUE #
            ################################
            self.doStopMutex.lock()
            if self.doStop:
                self.doStop = False
                self.doStopMutex.unlock()
                break
            self.doStopMutex.unlock()
            ################################
            ################################

            # Synchronize with other streams (if enabled for this stream)
            self.sharedImageBuffer.sync(self.deviceUrl)

            # Capture frame ( if available)
            if not self.cap.grab():
                if pause or not self.localVideo:
                    continue
                # Video End
                pause = True
                self.end.emit()
                continue

            # Retrieve frame
            _, self.grabbedFrame = self.cap.retrieve()
            # Add frame to buffer
            self.sharedImageBuffer.getByDeviceUrl(self.deviceUrl).add(self.grabbedFrame, self.dropFrameIfBufferFull)

            self.statsData.nFramesProcessed += 1
            # Inform GUI of updated statistics
            self.updateStatisticsInGUI.emit(self.statsData)

            # Limit fps
            delta = self.defaultTime - self.t.elapsed()
            # delta = self.defaultTime - self.captureTime
            if delta > 0:
                self.msleep(delta)
            # Save capture time
            self.captureTime = self.t.elapsed()

            # Update statistics
            self.updateFPS(self.captureTime)

            # Start timer (used to calculate capture rate)
            self.t.start()

        qDebug("Stopping capture thread...")

    def stop(self):
        with QMutexLocker(self.doStopMutex):
            self.doStop = True

    def connectToCamera(self):
        # Open camera
        camOpenResult = self.cap.open(self._deviceUrl, self.apiPreference)
        # Set resolution
        if self.width != -1:
            self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.width)
        if self.height != -1:
            self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.height)

        if camOpenResult:
            try:
                self.defaultTime = int(1000 / self.cap.get(cv2.CAP_PROP_FPS))
            except:
                self.defaultTime = 40
        # Return result
        return camOpenResult

    def disconnectCamera(self):
        # Camera is connected
        if self.cap.isOpened():
            # Disconnect camera
            self.cap.release()
            return True
        # Camera is NOT connected
        else:
            return False

    def isCameraConnected(self):
        return self.cap.isOpened()

    def getInputSourceWidth(self):
        return self.cap.get(cv2.CAP_PROP_FRAME_WIDTH)

    def getInputSourceHeight(self):
        return self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT)

    def updateFPS(self, timeElapsed):
        # Add instantaneous FPS value to queue
        if timeElapsed > 0:
            self.fps.put(1000 / timeElapsed)
            # Increment sample Number
            self.sampleNumber += 1

        # Maximum size of queue is DEFAULT_CAPTURE_FPS_STAT_QUEUE_LENGTH
        if self.fps.qsize() > CAPTURE_FPS_STAT_QUEUE_LENGTH:
            self.fps.get()
        # Update FPS value every DEFAULT_CAPTURE_FPS_STAT_QUEUE_LENGTH samples
        if self.fps.qsize() == CAPTURE_FPS_STAT_QUEUE_LENGTH and self.sampleNumber == CAPTURE_FPS_STAT_QUEUE_LENGTH:
            # Empty queue and store sum
            while not self.fps.empty():
                self.fpsSum += self.fps.get()
            # Calculate average FPS
            self.statsData.averageFPS = self.fpsSum / CAPTURE_FPS_STAT_QUEUE_LENGTH
            # Reset sum
            self.fpsSum = 0.0
            # Reset sample Number
            self.sampleNumber = 0
