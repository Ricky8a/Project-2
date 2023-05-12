from PyQt5.QtWidgets import QApplication

from RubixTimer import *

def main():
    app = QApplication([])
    window = MainWindow()
    window.show()
    app.exec()

if __name__ == '__main__':
    main()
