from PyQt5.QtWidgets import QMessageBox, QDialog
from PyQt5.QtCore import QRegExp, pyqtSignal
from PyQt5.QtGui import QRegExpValidator, QDoubleValidator

from ui_ImageProcessingSettingsDialog import Ui_ImageProcessingSettingsDialog
from Structures import *
from Config import *


class ImageProcessingSettingsDialog(QDialog, Ui_ImageProcessingSettingsDialog):
    newImageProcessingSettings = pyqtSignal(ImageProcessingSettings)

    def __init__(self, parent=None):
        super(ImageProcessingSettingsDialog, self).__init__(parent)
        # Setup dialog
        self.setupUi(self)
        # Initialize variables(s)
        self.imageProcessingSettings = ImageProcessingSettings()
        # Connect GUI signals and slots
        self.resetAllToDefaultsButton.released.connect(self.resetAllDialogToDefaults)
        self.resetSmoothToDefaultsButton.released.connect(self.resetSmoothDialogToDefaults)
        self.resetDilateToDefaultsButton.released.connect(self.resetDilateDialogToDefaults)
        self.resetErodeToDefaultsButton.released.connect(self.resetErodeDialogToDefaults)
        self.resetFlipToDefaultsButton.released.connect(self.resetFlipDialogToDefaults)
        self.resetCannyToDefaultsButton.released.connect(self.resetCannyDialogToDefaults)
        self.applyButton.released.connect(self.updateStoredSettingsFromDialog)
        self.smoothTypeGroup.buttonReleased.connect(self.smoothTypeChange)

        # dilateIterationsEdit input string validation
        rx5 = QRegExp("[1-9]\\d{0,2}")  # Integers 1 to 999
        validator5 = QRegExpValidator(rx5)
        self.dilateIterationsEdit.setValidator(validator5)
        # erodeIterationsEdit input string validation
        rx6 = QRegExp("[1-9]\\d{0,2}")  # Integers 1 to 999
        validator6 = QRegExpValidator(rx6)
        self.erodeIterationsEdit.setValidator(validator6)
        # cannyThresh1Edit input string validation
        rx7 = QRegExp("^[0-9]{1,3}$")  # Integers 0 to 999
        validator7 = QRegExpValidator(rx7)
        self.cannyThresh1Edit.setValidator(validator7)
        # cannyThresh2Edit input string validation
        rx8 = QRegExp("^[0-9]{1,3}$")  # Integers 0 to 999
        validator8 = QRegExpValidator(rx8)
        self.cannyThresh2Edit.setValidator(validator8)
        # cannyApertureSizeEdit input string validation
        rx9 = QRegExp("[3,5,7]")  # Integers 3, 5, 7
        validator9 = QRegExpValidator(rx9)
        self.cannyApertureSizeEdit.setValidator(validator9)
        # Set dialog values to defaults
        self.resetAllDialogToDefaults()
        # Update image processing settings in imageProcessingSettings structure and processingThread
        self.updateStoredSettingsFromDialog()

    def updateStoredSettingsFromDialog(self):
        # Validate values in dialog before storing
        self.validateDialog()
        # Smooth
        if self.smoothTypeGroup.checkedButton() == self.smoothBlurButton:
            self.imageProcessingSettings.smoothType = 0
        elif self.smoothTypeGroup.checkedButton() == self.smoothGaussianButton:
            self.imageProcessingSettings.smoothType = 1
        elif self.smoothTypeGroup.checkedButton() == self.smoothMedianButton:
            self.imageProcessingSettings.smoothType = 2
        self.imageProcessingSettings.smoothParam1 = int(self.smoothParam1Edit.text())
        self.imageProcessingSettings.smoothParam2 = int(self.smoothParam2Edit.text())
        self.imageProcessingSettings.smoothParam3 = float(self.smoothParam3Edit.text())
        self.imageProcessingSettings.smoothParam4 = float(self.smoothParam4Edit.text())
        # Dilate
        self.imageProcessingSettings.dilateNumberOfIterations = int(self.dilateIterationsEdit.text())
        # Erode
        self.imageProcessingSettings.erodeNumberOfIterations = int(self.erodeIterationsEdit.text())
        # Flip
        if self.flipCodeGroup.checkedButton() == self.flipXAxisButton:
            self.imageProcessingSettings.flipCode = 0
        elif self.flipCodeGroup.checkedButton() == self.flipYAxisButton:
            self.imageProcessingSettings.flipCode = 1
        elif self.flipCodeGroup.checkedButton() == self.flipBothAxesButton:
            self.imageProcessingSettings.flipCode = -1
        # Canny
        self.imageProcessingSettings.cannyThreshold1 = float(self.cannyThresh1Edit.text())
        self.imageProcessingSettings.cannyThreshold2 = float(self.cannyThresh2Edit.text())
        self.imageProcessingSettings.cannyApertureSize = int(self.cannyApertureSizeEdit.text())
        self.imageProcessingSettings.cannyL2gradient = self.cannyL2NormCheckBox.isChecked()
        # Update image processing flags in processingThread
        self.newImageProcessingSettings.emit(self.imageProcessingSettings)

    def updateDialogSettingsFromStored(self):
        # Smooth
        if self.imageProcessingSettings.smoothType == 0:
            self.smoothBlurButton.setChecked(True)
        elif self.imageProcessingSettings.smoothType == 1:
            self.smoothGaussianButton.setChecked(True)
        elif self.imageProcessingSettings.smoothType == 2:
            self.smoothMedianButton.setChecked(True)
        self.smoothParam1Edit.setText(str(self.imageProcessingSettings.smoothParam1))
        self.smoothParam2Edit.setText(str(self.imageProcessingSettings.smoothParam2))
        self.smoothParam3Edit.setText(str(self.imageProcessingSettings.smoothParam3))
        self.smoothParam4Edit.setText(str(self.imageProcessingSettings.smoothParam4))
        # Dilate
        self.dilateIterationsEdit.setText(str(self.imageProcessingSettings.dilateNumberOfIterations))
        # Erode
        self.erodeIterationsEdit.setText(str(self.imageProcessingSettings.erodeNumberOfIterations))
        # Flip
        if self.imageProcessingSettings.flipCode == 0:
            self.flipXAxisButton.setChecked(True)
        elif self.imageProcessingSettings.flipCode == 1:
            self.flipYAxisButton.setChecked(True)
        elif self.imageProcessingSettings.flipCode == -1:
            self.flipBothAxesButton.setChecked(True)
        # Canny
        self.cannyThresh1Edit.setText(str(self.imageProcessingSettings.cannyThreshold1))
        self.cannyThresh2Edit.setText(str(self.imageProcessingSettings.cannyThreshold2))
        self.cannyApertureSizeEdit.setText(str(self.imageProcessingSettings.cannyApertureSize))
        self.cannyL2NormCheckBox.setChecked(self.imageProcessingSettings.cannyL2gradient)
        #  Enable/disable appropriate Smooth parameter inputs
        self.smoothTypeChange(self.smoothTypeGroup.checkedButton())

    def resetAllDialogToDefaults(self):
        # Smooth
        self.resetSmoothDialogToDefaults()
        # Dilate
        self.resetDilateDialogToDefaults()
        # Erode
        self.resetErodeDialogToDefaults()
        # Flip
        self.resetFlipDialogToDefaults()
        # Canny
        self.resetCannyDialogToDefaults()

    def smoothTypeChange(self, input):
        if input == self.smoothBlurButton:
            # smoothParam1Edit input string validation
            rx1 = QRegExp("[1-9]\\d{0,2}")  # Integers 1 to 999
            validator1 = QRegExpValidator(rx1)
            self.smoothParam1Edit.setValidator(validator1)
            # smoothParam2Edit input string validation
            rx2 = QRegExp("[1-9]\\d{0,2}")  # Integers 1 to 999
            validator2 = QRegExpValidator(rx2)
            self.smoothParam2Edit.setValidator(validator2)
            # Enable / disable appropriate parameter inputs
            self.smoothParam1Edit.setEnabled(True)
            self.smoothParam2Edit.setEnabled(True)
            self.smoothParam3Edit.setEnabled(False)
            self.smoothParam4Edit.setEnabled(False)
            # Set parameter range labels
            self.smoothParam1RangeLabel.setText("[1-999]")
            self.smoothParam2RangeLabel.setText("[1-999]")
            self.smoothParam3RangeLabel.setText("")
            self.smoothParam4RangeLabel.setText("")
            # Set parameter labels
            self.smoothParam1Label.setText("Kernel Width")
            self.smoothParam2Label.setText("Kernel Height")
            self.smoothParam3Label.setText("")
            self.smoothParam4Label.setText("")
        elif input == self.smoothGaussianButton:
            # smoothParam1Edit input string validation
            rx1 = QRegExp("^[0-9]{1,2}$")  # Integers 0 to 99
            validator1 = QRegExpValidator(rx1)
            self.smoothParam1Edit.setValidator(validator1)
            # smoothParam2Edit input string validation
            rx2 = QRegExp("^[0-9]{1,2}$")  # Integers 0 to 99
            validator2 = QRegExpValidator(rx2)
            self.smoothParam2Edit.setValidator(validator2)
            # smoothParam3Edit input string validation
            validator3 = QDoubleValidator(0.0, 99.99, 2, self)
            validator3.setNotation(QDoubleValidator.StandardNotation)
            self.smoothParam3Edit.setValidator(validator3)
            # Enable / disable appropriate parameter inputs
            self.smoothParam1Edit.setEnabled(True)
            self.smoothParam2Edit.setEnabled(True)
            self.smoothParam3Edit.setEnabled(True)
            self.smoothParam4Edit.setEnabled(True)
            # Set parameter range labels
            self.smoothParam1RangeLabel.setText("[0-99]")
            self.smoothParam2RangeLabel.setText("[0-99]")
            self.smoothParam3RangeLabel.setText("[0.00-99.99]")
            self.smoothParam4RangeLabel.setText("[0.00-99.99]")
            # Set parameter labels
            self.smoothParam1Label.setText("Kernel Width")
            self.smoothParam2Label.setText("Kernel Height")
            self.smoothParam3Label.setText("Sigma X")
            self.smoothParam4Label.setText("Sigma Y")
        elif input == self.smoothMedianButton:
            # smoothParam1Edit input string validation
            rx1 = QRegExp("[1-9]\\d{0,1}")  # Integers 1 to 99
            validator1 = QRegExpValidator(rx1)
            self.smoothParam1Edit.setValidator(validator1)
            # Enable / disable appropriate parameter inputs
            self.smoothParam1Edit.setEnabled(True)
            self.smoothParam2Edit.setEnabled(False)
            self.smoothParam3Edit.setEnabled(False)
            self.smoothParam4Edit.setEnabled(False)
            # Set parameter range labels
            self.smoothParam1RangeLabel.setText("[1-99]")
            self.smoothParam2RangeLabel.setText("")
            self.smoothParam3RangeLabel.setText("")
            self.smoothParam4RangeLabel.setText("")
            # Set parameter labels
            self.smoothParam1Label.setText("Kernel (Square)")
            self.smoothParam2Label.setText("")
            self.smoothParam3Label.setText("")
            self.smoothParam4Label.setText("")

    def validateDialog(self):
        # Local variables
        inputEmpty = False

        # If value of Smooth parameter 1 is EVEN (and not zero), convert to ODD by adding 1
        if int(self.smoothParam1Edit.text()) % 2 == 0 and int(self.smoothParam1Edit.text()) != 0:
            self.smoothParam1Edit.setText(str(int(self.smoothParam1Edit.text()) + 1))
            QMessageBox.information(self.parentWidget(),
                                    "NOTE:",
                                    "Smooth parameter 1 must be an ODD number.\n\n"
                                    "Automatically set to (inputted value+1).")
        # If value of Smooth parameter 2 is EVEN (and not zero), convert to ODD by adding 1
        if int(self.smoothParam2Edit.text()) % 2 == 0 and int(self.smoothParam2Edit.text()) != 0:
            self.smoothParam2Edit.setText(str(int(self.smoothParam2Edit.text()) + 1))
            QMessageBox.information(self.parentWidget(),
                                    "NOTE:",
                                    "Smooth parameter 2 must be an ODD number (or zero).\n\n"
                                    "Automatically set to (inputted value+1).")
        # Check for empty inputs: if empty, set to default values
        if self.smoothParam1Edit.text().strip() == '':
            self.smoothParam1Edit.setText(str(DEFAULT_SMOOTH_PARAM_1))
            inputEmpty = True
        if self.smoothParam2Edit.text().strip() == '':
            self.smoothParam2Edit.setText(str(DEFAULT_SMOOTH_PARAM_2))
            inputEmpty = True
        if self.smoothParam3Edit.text().strip() == '':
            self.smoothParam3Edit.setText(str(DEFAULT_SMOOTH_PARAM_3))
            inputEmpty = True
        if self.smoothParam4Edit.text().strip() == '':
            self.smoothParam4Edit.setText(str(DEFAULT_SMOOTH_PARAM_4))
            inputEmpty = True
        if self.dilateIterationsEdit.text().strip() == '':
            self.dilateIterationsEdit.setText(str(DEFAULT_DILATE_ITERATIONS))
            inputEmpty = True
        if self.erodeIterationsEdit.text().strip() == '':
            self.erodeIterationsEdit.setText(str(DEFAULT_ERODE_ITERATIONS))
            inputEmpty = True
        if self.cannyThresh1Edit.text().strip() == '':
            self.cannyThresh1Edit.setText(str(DEFAULT_CANNY_THRESHOLD_1))
            inputEmpty = True
        if self.cannyThresh2Edit.text().strip() == '':
            self.cannyThresh2Edit.setText(str(DEFAULT_CANNY_THRESHOLD_2))
            inputEmpty = True
        if self.cannyApertureSizeEdit.text().strip() == '':
            self.cannyApertureSizeEdit.setText(str(DEFAULT_CANNY_APERTURE_SIZE))
            inputEmpty = True
        # Check if any of the inputs were empty
        if inputEmpty:
            QMessageBox.warning(self.parentWidget(),
                                "WARNING:",
                                "One or more inputs empty.\n\n"
                                "Automatically set to default values.")

        # Check for special parameter cases when smoothing type is GAUSSIAN
        if (self.smoothTypeGroup.checkedButton() == self.smoothGaussianButton
                and int(self.smoothParam1Edit.text()) == 0
                and float(self.smoothParam3Edit.text()) == 0.00):
            self.smoothParam1Edit.setText(str(DEFAULT_SMOOTH_PARAM_1))
            self.smoothParam3Edit.setText(str(DEFAULT_SMOOTH_PARAM_3))
            QMessageBox.warning(self.parentWidget(),
                                "ERROR:",
                                "Parameters 1 and 3 cannot BOTH be zero when the smoothing type is GAUSSIAN.\n\n"
                                "Automatically set to default values.")
        if (self.smoothTypeGroup.checkedButton() == self.smoothGaussianButton
                and int(self.smoothParam2Edit.text()) == 0
                and float(self.smoothParam4Edit.text()) == 0.00):
            self.smoothParam2Edit.setText(str(DEFAULT_SMOOTH_PARAM_2))
            self.smoothParam4Edit.setText(str(DEFAULT_SMOOTH_PARAM_4))
            QMessageBox.warning(self.parentWidget(),
                                "ERROR:",
                                "Parameters 2 and 4 cannot BOTH be zero when the smoothing type is GAUSSIAN.\n\n"
                                "Automatically set to default values.")

        # Ensure neither smoothing parameters 1 or 2 are ZERO (except in the GAUSSIAN case)
        if (self.smoothTypeGroup.checkedButton() != self.smoothGaussianButton
                and (int(self.smoothParam1Edit.text()) == 0 or float(self.smoothParam2Edit.text())) == 0):
            self.smoothParam1Edit.setText(str(DEFAULT_SMOOTH_PARAM_1))
            self.smoothParam2Edit.setText(str(DEFAULT_SMOOTH_PARAM_2))
            QMessageBox.warning(self.parentWidget(),
                                "ERROR:",
                                "Parameters 1 or 2 cannot be zero for the current smoothing type.\n\n"
                                "Automatically set to default values.")

    def resetSmoothDialogToDefaults(self):
        if DEFAULT_SMOOTH_TYPE == 0:
            self.smoothBlurButton.setChecked(True)
        elif DEFAULT_SMOOTH_TYPE == 1:
            self.smoothGaussianButton.setChecked(True)
        elif DEFAULT_SMOOTH_TYPE == 2:
            self.smoothMedianButton.setChecked(True)
        self.smoothParam1Edit.setText(str(DEFAULT_SMOOTH_PARAM_1))
        self.smoothParam2Edit.setText(str(DEFAULT_SMOOTH_PARAM_2))
        self.smoothParam3Edit.setText(str(DEFAULT_SMOOTH_PARAM_3))
        self.smoothParam4Edit.setText(str(DEFAULT_SMOOTH_PARAM_4))
        # Enable/disable appropriate Smooth parameter inputs
        self.smoothTypeChange(self.smoothTypeGroup.checkedButton())

    def resetDilateDialogToDefaults(self):
        self.dilateIterationsEdit.setText(str(DEFAULT_DILATE_ITERATIONS))

    def resetErodeDialogToDefaults(self):
        self.erodeIterationsEdit.setText(str(DEFAULT_ERODE_ITERATIONS))

    def resetFlipDialogToDefaults(self):
        if DEFAULT_FLIP_CODE == 0:
            self.flipXAxisButton.setChecked(True)
        elif DEFAULT_FLIP_CODE == 1:
            self.flipYAxisButton.setChecked(True)
        elif DEFAULT_FLIP_CODE == -1:
            self.flipBothAxesButton.setChecked(True)

    def resetCannyDialogToDefaults(self):
        self.cannyThresh1Edit.setText(str(DEFAULT_CANNY_THRESHOLD_1))
        self.cannyThresh2Edit.setText(str(DEFAULT_CANNY_THRESHOLD_2))
        self.cannyApertureSizeEdit.setText(str(DEFAULT_CANNY_APERTURE_SIZE))
        self.cannyL2NormCheckBox.setChecked(DEFAULT_CANNY_L2GRADIENT)
