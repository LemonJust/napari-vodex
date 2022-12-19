"""vodex_gui is a simple calculator built with Python and PyQt."""

import sys

from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget

WINDOW_SIZE = 500 #235


class VodexWindow(QMainWindow):
    """vodex_gui's main window (GUI or view)."""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("vodex_gui")
        self.setFixedSize(WINDOW_SIZE, WINDOW_SIZE)
        centralWidget = QWidget(self)
        self.setCentralWidget(centralWidget)


def main():
    """vodex_gui's main function."""
    vodexApp = QApplication([])
    vodexWindow = VodexWindow()
    vodexWindow.show()
    sys.exit(vodexApp.exec())


if __name__ == "__main__":
    main()
