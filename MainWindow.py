from PyQt5.QtWidgets import QMainWindow, QLabel, QPushButton, QMessageBox, QDialog, QTabWidget, QAbstractButton
from PyQt5.QtCore import Qt, QSize, pyqtSignal
import cv2

from ui_MainWindow import Ui_MainWindow
from SharedImageBuffer import SharedImageBuffer
from CameraConnectDialog import CameraConnectDialog
from CameraView import CameraView
from Buffer import *
from Config import *
from ModelBuffer import ModelBuffer
from UploadSql import SharedBoxesBuffer


class MainWindow(QMainWindow, Ui_MainWindow):
    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)
        # Setup UI
        self.setupUi(self)
        # Create dict instead of QMap
        self.deviceUrlDict = dict()
        self.cameraViewDict = dict()
        # Set start tab as blank
        newTab = QLabel(self.tabWidget)
        newTab.setText("No camera connected.")
        newTab.setAlignment(Qt.AlignCenter)
        self.tabWidget.addTab(newTab, "")
        self.tabWidget.setTabsClosable(False)
        # Add "Connect to Camera" button to tab
        self.connectToCameraButton = QPushButton()
        self.connectToCameraButton.setText("Connect to Camera...")
        self.tabWidget.setCornerWidget(self.connectToCameraButton, Qt.TopLeftCorner)
        self.connectToCameraButton.released.connect(self.connectToCamera)
        self.tabWidget.tabCloseRequested.connect(self.disconnectCamera)
        # Set focus on button
        self.connectToCameraButton.setFocus()
        # Connect other signals/slots
        self.actionAbout.triggered.connect(self.showAboutDialog)
        self.actionQuit.triggered.connect(self.close)
        self.actionFullScreen.toggled.connect(self.setFullScreen)
        # Create SharedImageBuffer object
        self.sharedImageBuffer = SharedImageBuffer()
        self.sharedBoxesBuffer = SharedBoxesBuffer()
        self.cameraNum = 0
        self.detector = ModelBuffer()
        self.tabWidget.currentChanged.connect(self.toShowByIndex)
        self.previousTab = None
        self.addCapPushButton_1.released.connect(lambda: self.addByPushButton(1))
        self.addCapPushButton_2.released.connect(lambda: self.addByPushButton(2))
        self.addCapPushButton_3.released.connect(lambda: self.addByPushButton(3))
        self.addCapPushButton_4.released.connect(lambda: self.addByPushButton(4))
        self.addCapPushButton_5.released.connect(lambda: self.addByPushButton(5))
        self.addCapPushButton_6.released.connect(lambda: self.addByPushButton(6))

    def toShowByIndex(self, index):
        # currentWidget = self.cameraViewDict[self.getFromDictByTabIndex(self.deviceUrlDict, index)]
        currentWidget = self.tabWidget.currentWidget()
        if isinstance(currentWidget, CameraView):
            if isinstance(self.previousTab, CameraView) and self.previousTab is not currentWidget:
                self.previousTab.doShowImage.emit(False)
            currentWidget.doShowImage.emit(True)
        self.previousTab = currentWidget

    def addByPushButton(self, idx):
        deviceUrl = CAP_URL[idx - 1]
        # Get next tab index
        nextTabIndex = 0 if len(self.deviceUrlDict) == 0 else self.tabWidget.count()
        # Check if this camera is already connected
        if not self.deviceUrlDict.__contains__(deviceUrl):
            # Create ImageBuffer with user-defined size
            imageBuffer = Buffer(DEFAULT_IMAGE_BUFFER_SIZE)
            # Add created ImageBuffer to SharedImageBuffer object
            self.sharedImageBuffer.add(deviceUrl, imageBuffer, self.actionSynchronizeStreams.isChecked())
            # Create CameraView
            cameraView = CameraView(self.tabWidget, deviceUrl, self.sharedImageBuffer, self.cameraNum,
                                    self.detector, self.sharedBoxesBuffer)

            # Check if stream synchronization is enabled
            if self.actionSynchronizeStreams.isChecked():
                # Prompt user
                ret = QMessageBox.question(self, "qt-opencv-multithreaded",
                                           "Stream synchronization is enabled.\n\n"
                                           "Do you want to start processing?\n\n"
                                           "Choose 'No' if you would like to open "
                                           "additional streams.",
                                           QMessageBox.Yes | QMessageBox.No, QMessageBox.Yes)
                # Start processing
                if ret == QMessageBox.Yes:
                    self.sharedImageBuffer.setSyncEnabled(True)
                # Defer processing
                else:
                    self.sharedImageBuffer.setSyncEnabled(False)

            # Attempt to connect to camera
            if cameraView.connectToCamera(DEFAULT_DROP_FRAMES, cv2.CAP_ANY, DEFAULT_CAP_THREAD_PRIO,
                                          DEFAULT_PROC_THREAD_PRIO, True, -1, -1):
                self.cameraNum += 1
                # Save tab label
                tabLabel = 'Cap%d' % idx
                # Allow tabs to be closed
                self.tabWidget.setTabsClosable(True)
                # If start tab, remove
                if nextTabIndex == 0:
                    self.tabWidget.removeTab(0)
                # Add tab
                self.tabWidget.addTab(cameraView, tabLabel)
                # Set tooltips
                self.setTabCloseToolTips(self.tabWidget, "Disconnect Camera")
                # Prevent user from enabling/disabling stream synchronization
                # after a camera has been connected
                self.actionSynchronizeStreams.setEnabled(False)
                # Add to map
                self.cameraViewDict[deviceUrl] = cameraView
                self.deviceUrlDict[deviceUrl] = nextTabIndex
                self.tabWidget.setCurrentWidget(cameraView)
                cameraView.setTabIndex(self.tabWidget.currentIndex())
                # cameraView.closeTabByIndex.connect(self.disconnectCamera)
            # Could not connect to camera
            else:
                # Display error message
                QMessageBox.warning(self,
                                    "ERROR:",
                                    "Could not connect to camera. "
                                    "Please check device deviceUrl.")
                # Explicitly delete widget
                cameraView.delete()
                # Remove from shared buffer
                self.sharedImageBuffer.removeByDeviceUrl(deviceUrl)
                # Explicitly delete ImageBuffer object
                del imageBuffer
            # Display error message
        else:
            QMessageBox.warning(self,
                                "ERROR:",
                                "Could not connect to camera. Already connected.")

    def connectToCamera(self):
        # We cannot connect to a camera if devices are already connected and stream synchronization is in progress
        if (self.actionSynchronizeStreams.isChecked()
                and len(self.deviceUrlDict) > 0
                and self.sharedImageBuffer.getSyncEnabled()):
            # Prompt user
            QMessageBox.warning(self, "qt-opencv-multithreaded",
                                "Stream synchronization is in progress.\n\n"
                                "Please close all currently open streams "
                                "before attempting to open a new stream.",
                                QMessageBox.Yes | QMessageBox.No, QMessageBox.Yes)
        # Attempt to connect to camera
        else:
            # Get next tab index
            nextTabIndex = 0 if len(self.deviceUrlDict) == 0 else self.tabWidget.count()
            # Show dialog
            cameraConnectDialog = CameraConnectDialog(self, self.actionSynchronizeStreams.isChecked())
            if cameraConnectDialog.exec() == QDialog.Accepted:
                # Save user-defined device deviceUrl
                deviceUrl = cameraConnectDialog.getDeviceUrl()
                # Check if this camera is already connected
                if not self.deviceUrlDict.__contains__(deviceUrl):
                    # Create ImageBuffer with user-defined size
                    imageBuffer = Buffer(cameraConnectDialog.getImageBufferSize())
                    # Add created ImageBuffer to SharedImageBuffer object
                    self.sharedImageBuffer.add(deviceUrl, imageBuffer, self.actionSynchronizeStreams.isChecked())
                    # Create CameraView
                    cameraView = CameraView(self.tabWidget, deviceUrl, self.sharedImageBuffer, self.cameraNum,
                                            self.detector, self.sharedBoxesBuffer)

                    # Check if stream synchronization is enabled
                    if self.actionSynchronizeStreams.isChecked():
                        # Prompt user
                        ret = QMessageBox.question(self, "qt-opencv-multithreaded",
                                                   "Stream synchronization is enabled.\n\n"
                                                   "Do you want to start processing?\n\n"
                                                   "Choose 'No' if you would like to open "
                                                   "additional streams.",
                                                   QMessageBox.Yes | QMessageBox.No, QMessageBox.Yes)
                        # Start processing
                        if ret == QMessageBox.Yes:
                            self.sharedImageBuffer.setSyncEnabled(True)
                        # Defer processing
                        else:
                            self.sharedImageBuffer.setSyncEnabled(False)

                    # Attempt to connect to camera
                    if cameraView.connectToCamera(
                            cameraConnectDialog.getDropFrameCheckBoxState(),
                            cameraConnectDialog.getApiPreference(),
                            cameraConnectDialog.getCaptureThreadPrio(),
                            cameraConnectDialog.getProcessingThreadPrio(),
                            cameraConnectDialog.getEnableFrameProcessingCheckBoxState(),
                            cameraConnectDialog.getResolutionWidth(),
                            cameraConnectDialog.getResolutionHeight()):

                        self.cameraNum += 1
                        # Save tab label
                        tabLabel = cameraConnectDialog.getTabLabel()
                        # Allow tabs to be closed
                        self.tabWidget.setTabsClosable(True)
                        # If start tab, remove
                        if nextTabIndex == 0:
                            self.tabWidget.removeTab(0)
                        # Add tab
                        self.tabWidget.addTab(cameraView, '%s [%s]' % (tabLabel, deviceUrl))
                        # Set tooltips
                        self.setTabCloseToolTips(self.tabWidget, "Disconnect Camera")
                        # Prevent user from enabling/disabling stream synchronization
                        # after a camera has been connected
                        self.actionSynchronizeStreams.setEnabled(False)
                        # Add to map
                        self.cameraViewDict[deviceUrl] = cameraView
                        self.deviceUrlDict[deviceUrl] = nextTabIndex
                        self.tabWidget.setCurrentWidget(cameraView)
                        cameraView.setTabIndex(self.tabWidget.currentIndex())
                        # cameraView.closeTabByIndex.connect(self.disconnectCamera)
                    # Could not connect to camera
                    else:
                        # Display error message
                        QMessageBox.warning(self,
                                            "ERROR:",
                                            "Could not connect to camera. "
                                            "Please check device deviceUrl.")
                        # Explicitly delete widget
                        cameraView.delete()
                        # Remove from shared buffer
                        self.sharedImageBuffer.removeByDeviceUrl(deviceUrl)
                        # Explicitly delete ImageBuffer object
                        del imageBuffer
                # Display error message
                else:
                    QMessageBox.warning(self,
                                        "ERROR:",
                                        "Could not connect to camera. Already connected.")

    def disconnectCamera(self, index):
        # Local variable(s)
        doDisconnect = True

        # Check if stream synchronization is enabled, more than 1 camera connected, and frame processing is not in progress
        if (self.actionSynchronizeStreams.isChecked()
                and len(self.cameraViewDict) > 1
                and not self.sharedImageBuffer.getSyncEnabled()):
            # Prompt user
            ret = QMessageBox.question(self,
                                       "qt-opencv-multithreaded",
                                       "Stream synchronization is enabled.\n\n"
                                       "Disconnecting this camera will cause frame "
                                       "processing to begin on other streams.\n\n"
                                       "Do you wish to proceed?",
                                       QMessageBox.Yes | QMessageBox.No, QMessageBox.Yes)
            # Do not disconnect
            if ret == QMessageBox.No:
                doDisconnect = False

        # Disconnect camera
        if doDisconnect:
            # Save deviceUrl of tabs
            nTabs = self.tabWidget.count()

            # Close tab
            self.tabWidget.removeTab(index)

            # get deviceUrl (key of dict)
            deviceUrl = self.getFromDictByTabIndex(self.deviceUrlDict, index)

            # Delete widget (CameraView) contained in tab
            self.cameraViewDict[deviceUrl].delete()

            # Remove from dict
            self.cameraViewDict.pop(deviceUrl)
            self.deviceUrlDict.pop(deviceUrl)

            # Update map (if tab closed is not last)
            if index != (nTabs - 1):
                self.updateDictValues(self.deviceUrlDict, index)

            # If start tab, set tab as blank
            if nTabs == 1:
                newTab = QLabel(self.tabWidget)
                newTab.setText("No camera connected.")
                newTab.setAlignment(Qt.AlignCenter)
                self.tabWidget.addTab(newTab, "")
                self.tabWidget.setTabsClosable(False)
                self.actionSynchronizeStreams.setEnabled(True)

    def showAboutDialog(self):
        QMessageBox.information(self, "About",
                                "Created by Nick D'Ademo\n\n"
                                "Contact: nickdademo@gmail.com\n"
                                "Website: www.nickdademo.com\n"
                                "Version: %s\n\n"
                                "Refactoring by Flyto\n\n" % APP_VERSION)

    # def removeFromDictByTabIndex(self, dic, tabIndex):
    #     for k, v in dic.items():
    #         if v == tabIndex:
    #             dic.pop(k)
    #             return True
    #     return False

    def getFromDictByTabIndex(self, dic, tabIndex):
        for k, v in dic.items():
            if v == tabIndex:
                return k

    def updateDictValues(self, dic, tabIndex):
        for k, v in dic.items():
            if v > tabIndex:
                dic[k] = v - 1

    def setFullScreen(self, flag):
        if flag:
            self.showFullScreen()
        else:
            self.showNormal()

    def setTabCloseToolTips(self, tabs, tooltip):
        for item in tabs.findChildren(QAbstractButton):
            if item.inherits("CloseButton"):
                item.setToolTip(tooltip)

    def closeEvent(self, event):
        self.sharedBoxesBuffer.cursor.close()
        self.sharedBoxesBuffer.connect.close()
        event.accept()
