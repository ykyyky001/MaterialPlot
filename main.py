import sys
from PySide2.QtCore import QFile, QRectF, QPointF
from PySide2.QtUiTools import QUiLoader
from PySide2.QtWidgets import QApplication, QMainWindow, QGraphicsScene, QFileDialog, QTreeView
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
        # TODO(ky): update button ui names to be consistent with each other.
        # suggest to use function as category, then followed by name.  
        # e.g. Plot_sel_ln, Action_open_cv
        self.ui.pushButton.clicked.connect(self.onClickGenPropChrt)
        self.ui.Plot_sel_ln.clicked.connect(self.onClickPlotSelLn)
        self.ui.actionOpen_CSV.triggered.connect(self.onActionOpenCSV)

#
# Button functions, called upon UI interactions. 
#

    def onClickGenPropChrt(self):
        print("Clicked!")
        self.drawEllipse()

    def onClickPlotSelLn(self):
        print("Now the selection line.")
        self.drawLine()

    def onActionOpenCSV(self):
        print("Ready to input data.")
        self.openCSV()

# 
# Internal functions.
# TODO(tn): wrap internal functions to another files when it gets larger.
# 
    def openCSV(self):
        filename, _ = QFileDialog.getOpenFileName(self, "Open CSV", filter="CSV Files (*.csv)")
        if filename:
            self.currentData.clear()
            with open(filename, "r") as f:
                csvrows = csv.DictReader(f)
                for index, row in enumerate(csvrows):
                    self.currentData.append(row)
            print(self.currentData)

    # TODO(team): make internal functions have general APIs that can be called by different
    # button functions.
    def drawLine(self):
        ecl = self.myScene.addLine(0,0,400,400,self.pen)

    def drawEllipse(self):
        self.myScene.clear()
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
