import sys
from PySide2.QtCore import QFile, QRectF, QPointF
from PySide2.QtUiTools import QUiLoader
from PySide2.QtWidgets import QApplication, QMainWindow, QGraphicsScene
from PySide2.QtGui import QBrush, QPen, QColor, QFont


class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        file = QFile("ashby.ui")
        file.open(QFile.ReadOnly)
        file.close()

        self.ui = QUiLoader().load(file)
        self.connectSignals()
        self.ui.show()

        self.myScene = QGraphicsScene()
        self.ui.graphicsView.setScene(self.myScene)

        self.pen = QPen(QColor(0,0,0))
        self.brush = QBrush(QColor(100,0,0, 100))
        self.brush2 = QBrush(QColor(100,100,0, 100))

    def connectSignals(self):
        self.ui.pushButton.clicked.connect(self.onClick)

    def onClick(self):
        print("clicked!")
        self.onGenerate()

    def onGenerate(self):
        ecl = self.myScene.addEllipse(QRectF(0, 0, 200, 100), self.pen, self.brush)
        text = self.myScene.addText("FatShe, Guaishow, and Ironman", QFont("Arial", 20, 2))

        ecl.setPos(QPointF(100, 100))
        text.setPos(QPointF(140, 170))

        ecl.setRotation(45)
        text.setRotation(45)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    sys.exit(app.exec_())
