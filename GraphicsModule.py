# -*- coding:utf-8 -*-
from typing import List

from PySide2.QtCore import QPointF, QRectF
from PySide2.QtGui import QBrush, QPen, QColor, QFont, QPolygonF

from DataModel import AshbyModel, MaterialItem
from GraphicTransformer import GraphicConfig, GraphicTransformer

class AshbyGraphicsController(object):
    def __init__(self, window, filename: str):
        self.window = window
        self.view = window.ui.graphicsView
        self.scene = window.myScene
        self.tree = window.ui.treeView
        self.pen = QPen(QColor(0, 0, 0))
        self.pen.setWidth(0)
        self.model = AshbyModel(filename)
        self.config = GraphicConfig()
        self.transformer = GraphicTransformer(self.config)
        # Store the semantic items which have been drawn on the plot, used when the config is updated.
        self.semanticItems = []

        self.initTreeView()
        self.connectSignals()

    #
    # Public
    #
    def updateConfig(self, expend_ratio: float=None, hull_sampling_step: int=None, log_scale: bool=None):
        self.config.updateConfig(expend_ratio, hull_sampling_step, log_scale)
        self.transformer = GraphicTransformer(self.config)
        self.updateGraphicItems()

    def clearScene(self):
        for item in self.view.graphicItems:
            self.scene.removeItem(item)
        # self.scene.clear()
        self.view.graphicItems.clear()
        self.semanticItems.clear()

    def drawAllMaterialEclipses(self):
        for name, info in self.model.getAllItems().items():
            self.drawEllipse(info)

    def drawFamilyHull(self):
        family_candidates = self.model.provideFamilyCandidateByColumn("Type")
        for family in family_candidates:
            items = self.model.getItemsByFamily("Type", family).values()
            self.drawHull(list(items))

    def drawAllHull(self):
        items = self.model.getAllItems().values()
        self.drawHull(list(items))

    def updateObjectsByAxis(self, new_column_info: List[List]):
        x_column_info = new_column_info[0]
        y_column_info = new_column_info[1]
        x_column = self.model.addProperty(x_column_info)
        y_column = self.model.addProperty(y_column_info)

        #TODO(tienan): implement the addtional logic.
        #Adjust the transformer to allow the flexibility of different x,y selection.
        print(x_column, x_column in self.model.getColumns())
        print(y_column, y_column in self.model.getColumns())

    #
    # Private
    #
    def connectSignals(self):
        self.tree.OnSelectionChanged.connect(self.OnTreeSelectionChanged)

    def OnTreeSelectionChanged(self, selections):
        # todo: make it do someing!
        print(selections)
        # anotherway to get
        selections = self.tree.getSelections()
        print(selections)

    def initTreeView(self):
        self.tree.clearModel()
        mattypes = self.model.getMaterialTypes()
        items = self.model.getAllItems()
        self.tree.addFamilies(mattypes)  # not necessary at all
        for item in items.values():
            self.tree.addItem(item, item.family)

    def drawEllipse(self, mat_item: MaterialItem):
        brush = QBrush(QColor(mat_item.color_r, mat_item.color_g, mat_item.color_b, a=255))
        elps = self.scene.addEllipse(self.transformer.matToSquare(mat_item), self.pen, brush)
        elps.setRotation(self.transformer.matRotation(mat_item))

        text = self.scene.addText(mat_item.label, QFont("Arial", 12, 2))
        text.setPos(self.transformer.matCenterPoint(mat_item))
        text.setRotation(self.transformer.matRotation(mat_item))
        # Append semantic item info for re-draw.
        # TODO(tienan): consider consolidate the two item caches together.
        self.semanticItems.append(mat_item)
        # Append graphic item info for view adjustment.
        self.view.graphicItems.extend((elps, text))

    def drawHull(self, items: List[MaterialItem]):
        if len(items) > 0:
            r, g, b = self.model.getMeanColor(items)
            self.pen = QPen(QColor(125, 125, 125, 50), 0)
            self.brush = QBrush(QColor(r, g, b, 100))
            poly = self.scene.addPolygon(self.transformer.getEllipseHull(items), self.pen, self.brush)
            poly.setZValue(-1)
            self.semanticItems.append(items)
            self.view.graphicItems.append(poly)

    def drawLine(self):
        # fake example, make your draw with your data
        self.scene.addLine(0, 0, 100, 400, self.pen)
        for i in range(self.model.getCount()):
            matitem = self.model.getItem(i)
            mean = matitem.getMean("Param3")
            std = matitem.getStd("Param3")
            # draw a cross
            graphicitem = self.scene.addLine(mean - 10, std - 10, mean + 10, std + 10, self.pen)
            graphicitem2 = self.scene.addLine(mean - 10, std + 10, mean + 10, std - 10, self.pen)

            self.view.graphicItems.append(graphicitem)  # not necessary at present, for further use
            self.view.graphicItems.append(graphicitem2)  # not necessary at present, for further use


    def updateGraphicItems(self):
        '''
        Iterates over the existing items and re-draw them with the latest config.
        '''
        prev_items = self.semanticItems.copy()
        self.clearScene()
        for item in prev_items:
            # If it is one item, draw the corresponding ellipse.
            if isinstance(item, MaterialItem):
                self.drawEllipse(item)
            # If it is a list of items, draw their convex hull.
            if isinstance(item, list):
                self.drawHull(item)