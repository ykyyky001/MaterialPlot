import sys
from PySide2.QtCore import QFile, QRectF, QPointF
from PySide2.QtUiTools import QUiLoader
from PySide2.QtWidgets import QApplication, QMainWindow, QGraphicsScene, QFileDialog
from PySide2.QtGui import QBrush, QPen, QColor, QFont
import csv


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
        self.currentData = []

    def connectSignals(self):
        self.ui.pushButton.clicked.connect(self.onClick_Gen_Prop_Chrt)
        self.ui.Plot_sel_ln.clicked.connect(self.onClick_SelLn)
        self.ui.actionOpen_CSV.triggered.connect(self.onOpenCSV)

    def onOpenCSV(self):
        filename, _ = QFileDialog.getOpenFileName(self, "Open CSV", filter="CSV Files (*.csv)")
        if filename:
            self.currentData.clear()
            with open(filename, "r") as f:
                csvrows = csv.DictReader(f)
                for index, row in enumerate(csvrows):
                    self.currentData.append(row)
            print(self.currentData)

    def onClick_Gen_Prop_Chrt(self):
        print("clicked!")
        self.onGenerate()

    def onGenerate(self):
        self.myScene.clear()
        ecl = self.myScene.addEllipse(QRectF(0, 0, 200, 100), self.pen, self.brush)
        text = self.myScene.addText("FatShe, Guaishow, and Ironman", QFont("Arial", 20, 2))

        ecl.setPos(QPointF(100, 100))
        text.setPos(QPointF(140, 170))

        ecl.setRotation(45)
        text.setRotation(45)

    def onClick_SelLn(self):
        print("now the selection line")
        self.onGenerate_SelLn()

    def onGenerate_SelLn(self):
        ecl = self.myScene.addLine(0,0,400,400,self.pen)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    sys.exit(app.exec_())
