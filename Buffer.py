from PyQt5.QtCore import QSemaphore, QMutex
from queue import Queue


class Buffer(object):
    def __init__(self, size):
        # Save buffer size
        self.bufferSize = size
        # Create semaphores
        self.freeSlots = QSemaphore(self.bufferSize)
        self.usedSlots = QSemaphore(0)
        self.clearBuffer_add = QSemaphore(1)
        self.clearBuffer_get = QSemaphore(1)
        # Create mutex
        self.queueProtect = QMutex()
        # Create queue
        self.queue = Queue(self.bufferSize)

    def add(self, data, dropIfFull=False):
        # Acquire semaphore
        self.clearBuffer_add.acquire()
        # If dropping is enabled, do not block if buffer is full
        if dropIfFull:
            # Try and acquire semaphore to add item

            # Drop new frame
            # if self.freeSlots.tryAcquire():
            #     # Add item to queue
            #     self.queueProtect.lock()
            #     self.queue.put(data)
            #     self.queueProtect.unlock()
            #     # Release semaphore
            #     self.usedSlots.release()

            # Drop oldest frame
            ret = self.freeSlots.tryAcquire()
            self.queueProtect.lock()
            if not ret:
                self.queue.get()
            else:
                # Release semaphore
                self.usedSlots.release()
            self.queue.put(data)
            self.queueProtect.unlock()
        # If buffer is full, wait on semaphore
        else:
            # Acquire semaphore
            self.freeSlots.acquire()
            # Add item to queue
            self.queueProtect.lock()
            self.queue.put(data)
            self.queueProtect.unlock()
            # Release semaphore
            self.usedSlots.release()
        # Release semaphore
        self.clearBuffer_add.release()

    def get(self):
        # Acquire semaphores
        self.clearBuffer_get.acquire()
        self.usedSlots.acquire()
        # Take item from queue
        self.queueProtect.lock()
        data = self.queue.get()
        self.queueProtect.unlock()
        # Release semaphores
        self.freeSlots.release()
        self.clearBuffer_get.release()
        # Return item to caller
        return data

    def clear(self):
        # Check if buffer contains items
        if self.queue.qsize() > 0:
            # Stop adding items to buffer (will return false if an item is currently being added to the buffer)
            if self.clearBuffer_add.tryAcquire():
                # Stop taking items from buffer (will return false if an item is currently being taken from the buffer)
                if self.clearBuffer_get.tryAcquire():
                    # Release all remaining slots in queue
                    self.freeSlots.release(self.queue.qsize())
                    # Acquire all queue slots
                    self.freeSlots.acquire(self.bufferSize)
                    # Reset usedSlots to zero
                    self.usedSlots.acquire(self.queue.qsize())
                    # Clear buffer
                    for _ in range(self.queue.qsize()):
                        self.queue.get()
                    # Release all slots
                    self.freeSlots.release(self.bufferSize)
                    # Allow get method to resume
                    self.clearBuffer_get.release()
                else:
                    return False
                # Allow add method to resume
                self.clearBuffer_add.release()
                return True
            else:
                return False
        else:
            return False

    def size(self):
        return self.queue.qsize()

    def maxSize(self):
        return self.bufferSize

    def isFull(self):
        return self.queue.qsize() == self.bufferSize

    def isEmpty(self):
        return self.queue.qsize() == 0
