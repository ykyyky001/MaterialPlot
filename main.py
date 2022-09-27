import sys
from PySide2.QtCore import QFile, QRectF, QPointF
from PySide2.QtUiTools import QUiLoader
from PySide2.QtWidgets import QApplication, QMainWindow, QGraphicsScene, QFileDialog, QTreeView
from PySide2.QtGui import QBrush, QPen, QColor, QFont
import csv

class simpleEclipse():
    def __init__(self, x, y, w, h, label, rotation = None):
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        self.rotation = rotation
        self.label = label
        self.printDebugString()

    def printDebugString(self):
        print(self.label, ": ",
              "x ", self.x, ", y ", self.y,
              ", w ", self.w, ", h ", self.h, 
              ", rotation ", self.rotation)


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
        self.currentData = []

    def connectSignals(self):
        self.ui.Plot_Prop_Chrt.clicked.connect(self.onClickGenPropChrt)
        self.ui.Plot_sel_ln.clicked.connect(self.onClickPlotSelLn)
        self.ui.Plot_clear.clicked.connect(self.onActionClear)
        # TODO(ky): update the ui nameing style in the menu to be consistent with the buttons.
        self.ui.actionOpen_CSV.triggered.connect(self.onActionOpenCSV)

#
# Button and menu functions, called upon UI interactions. 
#

    def onClickGenPropChrt(self):
        print("Clicked!")
        for raw_data in self.currentData:
            # TODO(team): make better naming for the csv columns.
            eclipse_info = simpleEclipse(x = float(raw_data["Param2_mean"]),
                                         y = float(raw_data["Param3_mean"]),
                                         w = float(raw_data["Param2_sd"]),
                                         h = float(raw_data["Param3_sd"]),
                                         label = raw_data["Name"])
            brush = QBrush(QColor(int(raw_data["Color_R"]),
                                  int(raw_data["Color_G"]),
                                  int(raw_data["Color_B"]),
                                  a = 100))
            self.drawEllipse(eclipse_info, brush)
            

    def onClickPlotSelLn(self):
        print("Now the selection line.")
        self.drawLine()

    def onActionOpenCSV(self):
        print("Ready to input data.")
        self.openCSV()

    def onActionClear(self):
        print("Graph cleared.")
        self.myScene.clear()

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

    def drawLine(self):
        line = self.myScene.addLine(0,0,400,400,self.pen)

    def drawEllipse(self, elps: simpleEclipse, brush: QBrush):
        elps_draw = self.myScene.addEllipse(QRectF(elps.x, elps.y, elps.w, elps.h), self.pen, brush)
        text = self.myScene.addText(elps.label, QFont("Arial", 12, 2))
        text.setPos(QPointF(elps.x, elps.y))
        if elps.rotation:
            elps_draw.setRotation(elps.rotation)
            text.setRotation(elps.rotation)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    sys.exit(app.exec_())
