from PyQt5.QtWidgets import QDialog, QMessageBox, QFileDialog
from PyQt5.QtCore import QRegExp, qDebug, QThread
from PyQt5.QtGui import QRegExpValidator
import cv2

from ui_CameraConnectDialog import Ui_CameraConnectDialog
from Config import *


class CameraConnectDialog(QDialog, Ui_CameraConnectDialog):
    def __init__(self, parent=None, isStreamSyncEnabled=False):
        super(CameraConnectDialog, self).__init__(parent)
        # Setup dialog
        self.setupUi(self)
        # deviceUrlEdit (device number) input validation
        # self.deviceUrlEdit.setValidator(QRegExpValidator(QRegExp("^[0-9]{1,3}$")))  # Integers 0 to 999
        # imageBufferSizeEdit (image buffer size) input validation
        self.imageBufferSizeEdit.setValidator(QRegExpValidator(QRegExp("^[0-9]{1,3}$")))  # Integers 0 to 999
        # resWEdit (resolution: width) input validation
        self.resWEdit.setValidator(QRegExpValidator(QRegExp("^[0-9]{1,4}$")))  # Integers 0 to 9999
        # resHEdit (resolution: height) input validation
        self.resHEdit.setValidator(QRegExpValidator(QRegExp("^[0-9]{1,4}$")))  # Integers 0 to 9999
        # Setup capture prio combo boxes
        self.apiPreference = {'CAP_ANY': cv2.CAP_ANY,
                              # 'CAP_VFW': cv2.CAP_VFW,
                              # 'CAP_V4L': cv2.CAP_V4L,
                              # 'CAP_V4L2': cv2.CAP_V4L2,
                              # 'CAP_FIREWIRE': cv2.CAP_FIREWIRE,
                              # 'CAP_FIREWARE': cv2.CAP_FIREWARE,
                              # 'CAP_IEEE1394': cv2.CAP_IEEE1394,
                              # 'CAP_DC1394': cv2.CAP_DC1394,
                              # 'CAP_CMU1394': cv2.CAP_CMU1394,
                              # 'CAP_QT': cv2.CAP_QT,
                              # 'CAP_UNICAP': cv2.CAP_UNICAP,
                              'CAP_DSHOW': cv2.CAP_DSHOW,
                              # 'CAP_PVAPI': cv2.CAP_PVAPI,
                              # 'CAP_OPENNI': cv2.CAP_OPENNI,
                              # 'CAP_OPENNI_ASUS': cv2.CAP_OPENNI_ASUS,
                              # 'CAP_ANDROID': cv2.CAP_ANDROID,
                              # 'CAP_XIAPI': cv2.CAP_XIAPI,
                              # 'CAP_AVFOUNDATION': cv2.CAP_AVFOUNDATION,
                              # 'CAP_GIGANETIX': cv2.CAP_GIGANETIX,
                              'CAP_MSMF': cv2.CAP_MSMF,
                              # 'CAP_WINRT': cv2.CAP_WINRT,
                              # 'CAP_INTELPERC': cv2.CAP_INTELPERC,
                              # 'CAP_OPENNI2': cv2.CAP_OPENNI2,
                              # 'CAP_OPENNI2_ASUS': cv2.CAP_OPENNI2_ASUS,
                              # 'CAP_GPHOTO2': cv2.CAP_GPHOTO2,
                              # 'CAP_GSTREAMER': cv2.CAP_GSTREAMER,
                              # 'CAP_FFMPEG': cv2.CAP_FFMPEG,
                              # 'CAP_IMAGES': cv2.CAP_IMAGES,
                              # 'CAP_ARAVIS': cv2.CAP_ARAVIS,
                              # 'CAP_OPENCV_MJPEG': cv2.CAP_OPENCV_MJPEG,
                              # 'CAP_INTEL_MFX': cv2.CAP_INTEL_MFX,
                              # 'CAP_XINE': cv2.CAP_XINE
                              }
        self.apiPreferenceComboBox.addItems(self.apiPreference.keys())
        # Setup capture prio combo boxes
        threadPriorities = ["Idle", "Lowest", "Low", "Normal", "High", "Highest", "Time Critical", "Inherit"]
        self.capturePrioComboBox.addItems(threadPriorities)
        self.processingPrioComboBox.addItems(threadPriorities)
        # Set dialog to defaults
        self.resetToDefaults()
        # Enable/disable checkbox
        self.enableFrameProcessingCheckBox.setEnabled(isStreamSyncEnabled)
        # Connect button to slot
        self.resetToDefaultsPushButton.released.connect(self.resetToDefaults)
        # Set Url Mode
        self.deviceUrlRadioButton.clicked.connect(lambda: self.setUrlMode('device url'))
        self.filenameRadioButton.clicked.connect(lambda: self.setUrlMode('filename'))
        self.rtspRadioButton.clicked.connect(lambda: self.setUrlMode('rtsp'))
        self.importFilePushButton.clicked.connect(self.openFile)

    def getDeviceUrl(self):
        # Set device number to default (any available camera) if field is blank
        if self.rtspRadioButton.isChecked():
            if (self.usernameEdit.text().strip() == ''
                    and self.passwordEdit.text().strip() == ''
                    and self.ipEdit.text().strip() == ''
                    and self.portEdit.text().strip() == ''
                    and self.channelsEdit.text().strip() == ''):
                ret = QMessageBox.question(self, "DEVICE_URL",
                                           DEFAULT_DEVICE_URL,
                                           QMessageBox.Yes | QMessageBox.No, QMessageBox.Yes)
                if ret:
                    qDebug('DEVICE_URL: %s' % DEFAULT_DEVICE_URL)
                    return DEFAULT_DEVICE_URL
                else:
                    QMessageBox.warning(self.parentWidget(),
                                        "WARNING:",
                                        "Device Url field blank.\n"
                                        "Automatically set to 0.")
                    return '0'
            else:
                return 'rtsp://%s:%s@%s:%s/Streaming/Channels/%s' \
                       % (self.usernameEdit.text(), self.passwordEdit.text(), self.ipEdit.text(), self.portEdit.text(),
                          self.channelsEdit.text())

        elif self.filenameRadioButton.isChecked():
            if self.filenameEdit.text().strip() == '':
                if DEFAULT_FILENAME.strip() == '':
                    QMessageBox.warning(self.parentWidget(),
                                        "WARNING:",
                                        "Device Url field blank.\n"
                                        "Automatically set to 0.")
                    return '0'
                else:
                    QMessageBox.warning(self.parentWidget(),
                                        "WARNING:",
                                        "Device Url field blank.\n"
                                        "Automatically set to %s." % DEFAULT_FILENAME)
                    return DEFAULT_FILENAME
            else:
                return self.filenameEdit.text()
        else:
            if self.deviceUrlEdit.text().strip() == '':
                QMessageBox.warning(self.parentWidget(),
                                    "WARNING:",
                                    "Device Url field blank.\n"
                                    "Automatically set to 0.")
                return '0'
            else:
                return self.deviceUrlEdit.text()

    def getResolutionWidth(self):
        # Return -1 if field is blank
        if self.resWEdit.text().strip() == '':
            return -1
        else:
            return int(self.resWEdit.text())

    def getResolutionHeight(self):
        # Return -1 if field is blank
        if self.resHEdit.text().strip() == '':
            return -1
        else:
            return int(self.resHEdit.text())

    def getImageBufferSize(self):
        # Set image buffer size to default if field is blank
        if self.imageBufferSizeEdit.text().strip() == '':
            QMessageBox.warning(self.parentWidget(),
                                "WARNING:",
                                "Image Buffer Size field blank.\n"
                                "Automatically set to default value.")
            return DEFAULT_IMAGE_BUFFER_SIZE
        # Set image buffer size to default if field is zero
        elif int(self.imageBufferSizeEdit.text()) == 0:
            QMessageBox.warning(self.parentWidget(),
                                "WARNING:",
                                "Image Buffer Size cannot be zero.\n"
                                "Automatically set to default value.")
            return DEFAULT_IMAGE_BUFFER_SIZE
        # Use image buffer size specified by user
        else:
            return int(self.imageBufferSizeEdit.text())

    def getDropFrameCheckBoxState(self):
        return self.dropFrameCheckBox.isChecked()

    def getApiPreference(self):
        return self.apiPreference.setdefault(self.apiPreferenceComboBox.currentText(), cv2.CAP_ANY)

    def getCaptureThreadPrio(self):
        return self.capturePrioComboBox.currentIndex()

    def getProcessingThreadPrio(self):
        return self.processingPrioComboBox.currentIndex()

    def getTabLabel(self):
        return self.tabLabelEdit.text()

    def getEnableFrameProcessingCheckBoxState(self):
        return self.enableFrameProcessingCheckBox.isChecked()

    def setUrlMode(self, mode):
        if mode == 'device url':
            self.deviceUrlEdit.setEnabled(True)
            self.filenameEdit.setEnabled(False)
            self.usernameEdit.setEnabled(False)
            self.passwordEdit.setEnabled(False)
            self.ipEdit.setEnabled(False)
            self.portEdit.setEnabled(False)
            self.channelsEdit.setEnabled(False)
            self.importFilePushButton.setEnabled(False)
            self.deviceUrlRadioButton.setChecked(True)
        elif mode == 'filename':
            self.deviceUrlEdit.setEnabled(False)
            self.filenameEdit.setEnabled(True)
            self.usernameEdit.setEnabled(False)
            self.passwordEdit.setEnabled(False)
            self.ipEdit.setEnabled(False)
            self.portEdit.setEnabled(False)
            self.channelsEdit.setEnabled(False)
            self.importFilePushButton.setEnabled(True)
            self.filenameRadioButton.setChecked(True)
        elif mode == 'rtsp':
            self.deviceUrlEdit.setEnabled(False)
            self.filenameEdit.setEnabled(False)
            self.usernameEdit.setEnabled(True)
            self.passwordEdit.setEnabled(True)
            self.ipEdit.setEnabled(True)
            self.portEdit.setEnabled(True)
            self.channelsEdit.setEnabled(True)
            self.importFilePushButton.setEnabled(False)
            self.rtspRadioButton.setChecked(True)

    def openFile(self):
        filename = QFileDialog.getOpenFileName(self.parent(), 'open file', '.', 'Excel files(*.mp4 , *.avi)')[0]
        self.filenameEdit.setText(filename)

    def resetToDefaults(self):
        # Default camera
        self.filenameEdit.clear()
        self.deviceUrlEdit.clear()
        self.usernameEdit.setText(DEFAULT_RTSP_USER)
        self.passwordEdit.setText(DEFAULT_RTSP_PASSWORD)
        self.ipEdit.setText(DEFAULT_RTSP_IP)
        self.portEdit.setText(DEFAULT_RTSP_PORT)
        self.channelsEdit.setText(DEFAULT_RTSP_CAHHELS)
        self.setUrlMode(DEFAULT_URL_MODE)
        # Resolution
        self.resWEdit.clear()
        self.resHEdit.clear()
        # Image buffer size
        self.imageBufferSizeEdit.setText(str(DEFAULT_IMAGE_BUFFER_SIZE))
        # Drop frames
        self.dropFrameCheckBox.setChecked(DEFAULT_DROP_FRAMES)
        # apiPreference
        self.apiPreferenceComboBox.setCurrentText(DEFAULT_APIPREFERENCE)
        # Capture thread
        if DEFAULT_CAP_THREAD_PRIO == QThread.IdlePriority:
            self.capturePrioComboBox.setCurrentIndex(0)
        elif DEFAULT_CAP_THREAD_PRIO == QThread.LowestPriority:
            self.capturePrioComboBox.setCurrentIndex(1)
        elif DEFAULT_CAP_THREAD_PRIO == QThread.LowPriority:
            self.capturePrioComboBox.setCurrentIndex(2)
        elif DEFAULT_CAP_THREAD_PRIO == QThread.NormalPriority:
            self.capturePrioComboBox.setCurrentIndex(3)
        elif DEFAULT_CAP_THREAD_PRIO == QThread.HighPriority:
            self.capturePrioComboBox.setCurrentIndex(4)
        elif DEFAULT_CAP_THREAD_PRIO == QThread.HighestPriority:
            self.capturePrioComboBox.setCurrentIndex(5)
        elif DEFAULT_CAP_THREAD_PRIO == QThread.TimeCriticalPriority:
            self.capturePrioComboBox.setCurrentIndex(6)
        elif DEFAULT_CAP_THREAD_PRIO == QThread.InheritPriority:
            self.capturePrioComboBox.setCurrentIndex(7)
        # Processing thread
        if DEFAULT_PROC_THREAD_PRIO == QThread.IdlePriority:
            self.processingPrioComboBox.setCurrentIndex(0)
        elif DEFAULT_PROC_THREAD_PRIO == QThread.LowestPriority:
            self.processingPrioComboBox.setCurrentIndex(1)
        elif DEFAULT_PROC_THREAD_PRIO == QThread.LowPriority:
            self.processingPrioComboBox.setCurrentIndex(2)
        elif DEFAULT_PROC_THREAD_PRIO == QThread.NormalPriority:
            self.processingPrioComboBox.setCurrentIndex(3)
        elif DEFAULT_PROC_THREAD_PRIO == QThread.HighPriority:
            self.processingPrioComboBox.setCurrentIndex(4)
        elif DEFAULT_PROC_THREAD_PRIO == QThread.HighestPriority:
            self.processingPrioComboBox.setCurrentIndex(5)
        elif DEFAULT_PROC_THREAD_PRIO == QThread.TimeCriticalPriority:
            self.processingPrioComboBox.setCurrentIndex(6)
        elif DEFAULT_PROC_THREAD_PRIO == QThread.InheritPriority:
            self.processingPrioComboBox.setCurrentIndex(7)
        # Tab label
        self.tabLabelEdit.setText("")
        # Enable Frame Processing checkbox
        self.enableFrameProcessingCheckBox.setChecked(True)
