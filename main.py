import sys

from PyQt5.QtWidgets import QApplication
import qdarkstyle

from MainWindow import MainWindow


def main():
    app = QApplication(sys.argv)
    win = MainWindow()

    # Setup style
    app.setStyleSheet(qdarkstyle.load_stylesheet_pyqt5())

    # Show main window
    win.show()

    # Start event loop
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
