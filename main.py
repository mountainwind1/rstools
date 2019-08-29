#
#
#
import sys
#from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QApplication
from app import MainWindow

def main():
    app = QApplication(sys.argv)
    win = MainWindow()
    win.show()
    win.raise_()
    sys.exit(app.exec_())
if __name__ == "__main__":
    main()
