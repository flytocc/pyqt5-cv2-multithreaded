from PyQt5.QtCore import QMutexLocker, QMutex, QWaitCondition


class SharedImageBuffer(object):
    def __init__(self):
        # Initialize variables(s)
        self.nArrived = 0
        self.doSync = False
        self.syncSet = set()
        self.wc = QWaitCondition()
        self.imageBufferDict = dict()
        self.mutex = QMutex()

    def add(self, deviceUrl, imageBuffer, sync=False):
        # Device stream is to be synchronized
        if sync:
            with QMutexLocker(self.mutex):
                self.syncSet.add(deviceUrl)
        # Add image buffer to map
        self.imageBufferDict[deviceUrl] = imageBuffer

    def getByDeviceUrl(self, deviceUrl):
        return self.imageBufferDict[deviceUrl]

    def removeByDeviceUrl(self, deviceUrl):
        # Remove buffer for device from imageBufferDict
        self.imageBufferDict.pop(deviceUrl)

        # Also remove from syncSet (if present)
        with QMutexLocker(self.mutex):
            if self.syncSet.__contains__(deviceUrl):
                self.syncSet.remove(deviceUrl)
                self.wc.wakeAll()

    def sync(self, deviceUrl):
        # Only perform sync if enabled for specified device/stream
        self.mutex.lock()
        if self.syncSet.__contains__(deviceUrl):
            # Increment arrived count
            self.nArrived += 1
            # We are the last to arrive: wake all waiting threads
            if self.doSync and self.nArrived == len(self.syncSet):
                self.wc.wakeAll()
            # Still waiting for other streams to arrive: wait
            else:
                self.wc.wait(self.mutex)
            # Decrement arrived count
            self.nArrived -= 1
        self.mutex.unlock()

    def wakeAll(self):
        with QMutexLocker(self.mutex):
            self.wc.wakeAll()

    def setSyncEnabled(self, enable):
        self.doSync = enable

    def isSyncEnabledForDeviceUrl(self, deviceUrl):
        return self.syncSet.__contains__(deviceUrl)

    def getSyncEnabled(self):
        return self.doSync

    def containsImageBufferForDeviceUrl(self, deviceUrl):
        return self.imageBufferDict.__contains__(deviceUrl)
