from PyQt5.QtWidgets import QApplication
import qdarkstyle
import sys

import _init_paths  # pylint: disable=unused-import
from MainWindow import MainWindow

def main():
    app = QApplication(sys.argv)
    win = MainWindow()
    # setup qdarkstyle
    app.setStyleSheet(qdarkstyle.load_stylesheet_pyqt5())
    # Show main window
    win.show()
    # Start event loop
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
