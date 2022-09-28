# -*- coding:utf-8 -*-
import sys
from PySide2.QtCore import QFile, QRectF, QPointF
from PySide2.QtUiTools import QUiLoader
from PySide2.QtWidgets import QApplication, QMainWindow, QGraphicsScene, QFileDialog, QTreeView
from PySide2.QtGui import QBrush, QPen, QColor, QFont
import csv
from GraphicsModule import AshbyGraphicsController
from View.AGraphicsView import AGraphicsView
app = None

class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        file = QFile("ashby.ui")
        file.open(QFile.ReadOnly)
        file.close()
        loader = QUiLoader()
        loader.registerCustomWidget(AGraphicsView)
        self.ui = loader.load(file)
        self.connectSignals()
        self.ui.show()
        self.csv_fpath = None
        self.myScene = QGraphicsScene()
        self.ui.graphicsView.setScene(self.myScene)
        self.controller = AshbyGraphicsController(self.myScene, self.csv_fpath)

        self.pen = QPen(QColor(0,0,0))
        self.ui.graphicsView.resetView()
        self.ui.graphicsView.initHelperItems()

    def connectSignals(self):
        self.ui.Plot_Prop_Chrt.clicked.connect(self.onClickGenPropChrt)
        self.ui.Plot_sel_ln.clicked.connect(self.onClickPlotSelLn)
        self.ui.Plot_clear.clicked.connect(self.onActionClear)
        # TODO(ky): update the ui nameing style in the menu to be consistent with the buttons.
        self.ui.actionOpen_CSV.triggered.connect(self.onActionOpenCSV)
        self.ui.actionHotReload.triggered.connect(self.onActionHotReload)
        self.ui.actionConvexHull.triggered.connect(self.onActionConvexHull)
        self.ui.actionGenerateChart.triggered.connect(self.onClickGenPropChrt)
        self.ui.actionFamilyBubble.triggered.connect(self.onActionConvexHull)
        self.ui.actionPlotSelLn.triggered.connect(self.onClickPlotSelLn)
        self.ui.actionResetView.triggered.connect(self.onResetView)
#
# Button and menu functions, called upon UI interactions.
#
    def onResetView(self):
        self.ui.graphicsView.resetView()
        app.processEvents()

    def onActionHotReload(self):
        '''
        Hot reloads the code modules. For debug purpose.
        '''
        from HotReloadModule import reloadModules
        reloadModules()
        from GraphicsModule import AshbyGraphicsController
        self.controller = AshbyGraphicsController(self.myScene, self.csv_fpath)

    def onClickGenPropChrt(self):
        '''
        Draws all existing materials onto the plot.
        '''
        self.onActionClear()
        self.controller.drawAllMaterialEclipses()

    def onActionOpenCSV(self):
        '''
        Loads data, updates both the model and controller.
        '''
        print("Ready to input data.")
        filename, _ = QFileDialog.getOpenFileName(self, "Open CSV", filter="CSV Files (*.csv)")
        if filename:
            self.csv_fpath = filename
        self.controller = AshbyGraphicsController(self.myScene, self.csv_fpath)

    def onClickPlotSelLn(self):
        self.controller.drawLine()

    def onActionClear(self):
        print("Graph cleared.")
        self.controller.clearScene()
        self.ui.graphicsView.resetView()
        
    def onActionConvexHull(self):
        self.controller.drawAllHull()
        # self.controller.drawFamilyHull()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    sys.exit(app.exec_())
