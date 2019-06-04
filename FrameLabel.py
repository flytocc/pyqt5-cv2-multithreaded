from PyQt5.QtWidgets import QLabel, QMenu, QAction
from PyQt5.QtCore import QPoint, pyqtSignal, Qt
from PyQt5.QtGui import QPainter

from Structures import *


class FrameLabel(QLabel):
    newMouseData = pyqtSignal(MouseData)
    onMouseMoveEvent = pyqtSignal()

    def __init__(self, parent=None):
        super(FrameLabel, self).__init__(parent)
        self.menu = None
        self.mouseData = MouseData()
        self.startPoint = QPoint()
        self.mouseCursorPos = QPoint()
        self.drawBox = False
        self.box = QRect()

        self.startPoint.setX(0)
        self.startPoint.setY(0)
        self.mouseCursorPos.setX(0)
        self.mouseCursorPos.setY(0)
        self.mouseData.leftButtonRelease = False
        self.mouseData.rightButtonRelease = False
        self.createContextMenu()

    def mouseMoveEvent(self, ev):
        # Save mouse cursor position
        self.setMouseCursorPos(ev.pos())  # QPoint
        # Update box width and height if box drawing is in progress
        if self.drawBox:
            self.box.setWidth(self.getMouseCursorPos().x() - self.startPoint.x())
            self.box.setHeight(self.getMouseCursorPos().y() - self.startPoint.y())
        # Inform main window of mouse move event
        self.onMouseMoveEvent.emit()

    def setMouseCursorPos(self, data):
        self.mouseCursorPos = data

    def getMouseCursorPos(self):
        return self.mouseCursorPos

    def mouseReleaseEvent(self, ev):
        # Update cursor position
        self.setMouseCursorPos(ev.pos())
        # On left mouse button release
        if ev.button() == Qt.LeftButton:
            # Set leftButtonRelease flag to True
            self.mouseData.leftButtonRelease = True
            if self.drawBox:
                # Stop drawing box
                self.drawBox = False
                # Save box dimensions
                self.mouseData.selectionBox.setX(self.box.left())
                self.mouseData.selectionBox.setY(self.box.top())
                self.mouseData.selectionBox.setWidth(self.box.width())
                self.mouseData.selectionBox.setHeight(self.box.height())
                # Set leftButtonRelease flag to True
                self.mouseData.leftButtonRelease = True
                # Inform main window of event
                self.newMouseData.emit(self.mouseData)
            # Set leftButtonRelease flag to False
            self.mouseData.leftButtonRelease = False
        # On right mouse button release
        elif ev.button() == Qt.RightButton:
            # If user presses (and then releases) the right mouse button while drawing box, stop drawing box
            if self.drawBox:
                self.drawBox = False
            else:
                # Show context menu
                self.menu.exec(ev.globalPos())

    def mousePressEvent(self, ev):
        # Update cursor position
        self.setMouseCursorPos(ev.pos())
        if ev.button() == Qt.LeftButton:
            # Start drawing box
            self.startPoint = ev.pos()
            self.box = QRect(self.startPoint.x(), self.startPoint.y(), 0, 0)
            self.drawBox = True

    def paintEvent(self, ev):
        QLabel.paintEvent(self, ev)
        painter = QPainter(self)
        # Draw box
        if self.drawBox:
            painter.setPen(Qt.blue)
            painter.drawRect(self.box)

    def createContextMenu(self):
        # Create top-level menu object
        self.menu = QMenu(self)
        # Add actions
        action = QAction(self)
        action.setText("Reset ROI")
        self.menu.addAction(action)
        action = QAction(self)
        action.setText("Scale to Fit Frame")
        action.setCheckable(True)
        self.menu.addAction(action)
        self.menu.addSeparator()
        # Create image processing menu object
        menu_imgProc = QMenu(self)
        menu_imgProc.setTitle("Image Processing")
        self.menu.addMenu(menu_imgProc)
        # Add actions
        action = QAction(self)
        action.setText("Grayscale")
        action.setCheckable(True)
        menu_imgProc.addAction(action)
        action = QAction(self)
        action.setText("Smooth")
        action.setCheckable(True)
        menu_imgProc.addAction(action)
        action = QAction(self)
        action.setText("Dilate")
        action.setCheckable(True)
        menu_imgProc.addAction(action)
        action = QAction(self)
        action.setText("Erode")
        action.setCheckable(True)
        menu_imgProc.addAction(action)
        action = QAction(self)
        action.setText("Flip")
        action.setCheckable(True)
        menu_imgProc.addAction(action)
        action = QAction(self)
        action.setText("Canny")
        action.setCheckable(True)
        menu_imgProc.addAction(action)
        menu_imgProc.addSeparator()
        action = QAction(self)
        action.setText("Settings...")
        menu_imgProc.addAction(action)
