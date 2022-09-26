import sys
from PySide2.QtCore import QFile
from PySide2.QtUiTools import QUiLoader
from PySide2.QtWidgets import QApplication, QMainWindow


class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        file = QFile("ashby.ui")
        file.open(QFile.ReadOnly)
        file.close()

        self.ui = QUiLoader().load(file)
        self.ui.show()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    sys.exit(app.exec_())
