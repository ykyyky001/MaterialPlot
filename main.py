# -*- coding:utf-8 -*-
import sys
from typing import List

from PySide2.QtCore import QFile, QRectF, QPointF
from PySide2.QtUiTools import QUiLoader
from PySide2.QtWidgets import QApplication, QMainWindow, QGraphicsScene, QFileDialog, QTreeView, QDialog
from PySide2.QtGui import QBrush, QPen, QColor, QFont

from GraphicsModule import AshbyGraphicsController
from View.AGraphicsView import AGraphicsView
from View.TreeView import TreeView

app = None


class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        file = QFile("ashby.ui")
        file.open(QFile.ReadOnly)
        file.close()
        loader = QUiLoader()
        loader.registerCustomWidget(AGraphicsView)
        loader.registerCustomWidget(TreeView)
        self.ui = loader.load(file)
        self.connectSignals()
        self.ui.show()
        self.csv_fpath = None
        self.myScene = QGraphicsScene()
        self.ui.graphicsView.setScene(self.myScene)
        self.controller = AshbyGraphicsController(self, self.csv_fpath)

        self.pen = QPen(QColor(0, 0, 0))
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
        self.ui.actionFitView.triggered.connect(self.onFitView)
        self.ui.buttonGroup.buttonToggled.connect(self.onAxisStyleChanged)
        self.ui.actionAxes.triggered.connect(self.onDefineAxes)

    #
    # Button and menu functions, called upon UI interactions.
    #

    def onDefineAxes(self):
        available_columns = self.controller.model.getColumns()
        # TODO(kaiyang): add UI to actual handle the logic of column selection.
        self.popupAxes = setAxesPopUp(available_columns)
        self.popupAxes.display()
        #how to ask the setAxes window to display?
        self.controller.updateObjectsByAxis(x_column = available_columns[0],
                                            y_column = available_columns[1])

    def onAxisStyleChanged(self, _):
        if self.ui.linearRadio.isChecked():
            self.controller.updateConfig(log_scale=False)
            self.ui.graphicsView.changeAxisMode(0)
        else:
            self.controller.updateConfig(log_scale=True)
            self.ui.graphicsView.changeAxisMode(1)
        self.onFitView()

    def onResetView(self):
        self.ui.graphicsView.resetView()
        app.processEvents()

    def onFitView(self):
        self.ui.graphicsView.fitView()
        app.processEvents()

    def onActionHotReload(self):
        '''
        Hot reloads the code modules. For debug purpose.
        '''
        from HotReloadModule import reloadModules
        reloadModules()
        from GraphicsModule import AshbyGraphicsController
        from DataModel import AshbyModel
        self.controller = AshbyGraphicsController(self, self.csv_fpath)

    def onClickGenPropChrt(self):
        '''
        Draws all existing materials onto the plot.
        '''
        self.onActionClear()
        self.controller.drawAllMaterialEclipses()
        self.onFitView()

    def onActionOpenCSV(self):
        '''
        Loads data, updates both the model and controller.
        '''
        print("Ready to input data.")
        filename, _ = QFileDialog.getOpenFileName(self, "Open CSV", filter="CSV Files (*.csv)")
        if filename:
            self.csv_fpath = filename
        self.controller = AshbyGraphicsController(self, self.csv_fpath)

    def onClickPlotSelLn(self):
        self.controller.drawLine()

    def onActionClear(self):
        print("Graph cleared.")
        self.controller.clearScene()
        self.ui.graphicsView.resetView()

    def onActionConvexHull(self):
        self.controller.drawAllHull()
        # self.controller.drawFamilyHull()

class setAxesPopUp(QDialog):

    def __init__(self, column_candidates: List[str]):
        super().__init__()
        file = QFile("Axes.ui")
        file.open(QFile.ReadOnly)
        file.close()
        loader = QUiLoader()
        self.ui = loader.load(file)
        self.ui.show()
        self.Main = MainWindow
        #need to populate the list from the column title, withouth the _mean/_sd
        #no sure what the index does.... maybe helpful maybe not
        self.propList = self.columnCandidateFilter(column_candidates)
        self.ui.x_n.addItems(self.propList)
        self.ui.x_d.addItems(self.propList)
        self.ui.y_n.addItems(self.propList)
        self.ui.y_d.addItems(self.propList)
        self.ui.buttonBox.accepted.connect(self.passingInfo)
        self.ui.buttonBox.rejected.connect(self.close)
    def passingInfo(self):
        #here read users input and bring back the info of x and y axes
        #n stands for numerator, d stands for denominator
        x_n = self.ui.x_n.currentText()
        y_n = self.ui.y_n.currentText()
        x_d = self.ui.x_d.currentText()
        y_d = self.ui.y_d.currentText()
        self.newX = [x_n, self.ui.x_nExp.text(),x_d, self.ui.x_dExp.text()]
        self.newY = [y_n, self.ui.y_nExp.text(),y_d, self.ui.y_dExp.text()]
        print(self.newX)
        print(self.newY)
        return self.newX, self.newY

    def display(self):
        self.ui.show()

    @staticmethod
    def columnCandidateFilter(candidates: List[str]):
        #TODO(ky): do something here.
        return candidates

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    sys.exit(app.exec_())
