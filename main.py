
#
#
#
import sys
#from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QApplication, QDesktopWidget
from rstools.app import MainWindow
from rstools.utils import newIcon


def center(self):
    qr = self.frameGeometry()
    cp = QDesktopWidget().availableGeometry().center()
    qr.moveCenter(cp)
    self.move(qr.topLeft())

def main():
    app = QApplication(sys.argv)
    app.setWindowIcon(newIcon('sat'))
    win = MainWindow()
    #win.resize(1000, 800)
    center(win)
    win.show()

    win.raise_()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()

