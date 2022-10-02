# -*- coding:utf-8 -*-
from math import log10
from typing import List

import numpy as np
from PySide2.QtCore import QRectF
from PySide2.QtGui import QBrush, QPen, QColor, QFont, QPolygonF
from PySide2.QtCore import QPointF

from AlgorithmUtils import ellipseHull, simpleEllipse
from DataModel import AshbyModel, MaterialItem


class GraphicConfig():
    '''
    Describe the plot features.
    '''

    def __init__(self):
        self.expend_ratio = 2.
        self.hull_sampling_step = 200
        self.log_scale = True

    def update_config(self, expend_ratio: float=None,
                      hull_sampling_step: int=None, log_scale: bool=None):
        # Updates can be optional. Only update the config values which are explicitly passed in.
        if expend_ratio:
            self.expend_ratio = expend_ratio
        if hull_sampling_step:
            self.hull_sampling_step = hull_sampling_step
        if log_scale is not None:
            self.log_scale = log_scale


class GraphicTransformer():
    '''
    Converts the coordinate-related features to the appropriate plot scale based on the config.
    Note the final Qt objects have negative y values to fit the y-axis style in the plot.
    '''

    def __init__(self, config: GraphicConfig):
        self.config = config

    def matToSquare(self, mat_item: MaterialItem):
        elps = self.convertMatToSimpleEllipse(mat_item)
        return QRectF(elps.upper_left_x, elps.upper_left_y, elps.w, elps.h)

    def matUpperLeftPoint(self, mat_item: MaterialItem):
        elps = self.convertMatToSimpleEllipse(mat_item)
        return QPointF(elps.upper_left_x, elps.upper_left_y)

    def matCenterPoint(self, mat_item: MaterialItem):
        elps = self.convertMatToSimpleEllipse(mat_item)
        return QPointF(elps.x, elps.y)

    def matRotation(self, mat_item: MaterialItem):
        elps = self.convertMatToSimpleEllipse(mat_item)
        return elps.rotation

    def getEllipseHull(self, items: List[MaterialItem]):
        hull_v = ellipseHull([self.convertMatToSimpleEllipse(item) for item in items],
                           self.config.expend_ratio,
                           self.config.hull_sampling_step)
        return QPolygonF(list(map(QPointF, *hull_v.T)))

    #
    # Private
    #
    def convertMatToSimpleEllipse(self, mat_item: MaterialItem):
        '''
        Convert an material item to a pure geometry object.
        '''
        upper_left_x = mat_item.x - mat_item.w / 2.
        # Specific handling of y-coor (is a negative value) because we actually mark
        # the neg-y area on the plot as pos-y for visualization purpose.
        upper_left_y = - mat_item.y - mat_item.h / 2.
        width = mat_item.w
        height = mat_item.h
        if self.config.log_scale:
            # The ellipse/square in log scale is defined by the log of the original four corner points.
            # Use the diff between the lower-right point and upper-left point to re-calculate
            # the width and height.
            width = log10(upper_left_x + width) - log10(upper_left_x)
            height = log10(-upper_left_y) - log10(-(upper_left_y - height))
            upper_left_x = log10(upper_left_x)
            upper_left_y = -log10(-upper_left_y)
        center_x = upper_left_x + width / 2.
        center_y = upper_left_y + height / 2.
        return simpleEllipse(center_x, center_y, width, height, mat_item.rotation)


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

        self.initTreeView()
        self.connectSignals()

    #
    # Public
    #
    def update_config(self, expend_ratio: float=None, hull_sampling_step: int=None, log_scale: bool=None):
        self.config.update_config(expend_ratio, hull_sampling_step, log_scale)
        self.transformer = GraphicTransformer(self.config)
        self.clearScene()

    def clearScene(self):
        for item in self.view.graphicItems:
            self.scene.removeItem(item)
        # self.scene.clear()
        self.view.graphicItems.clear()

    def drawAllMaterialEclipses(self):
        for name, info in self.model.getAllItems().items():
            self.drawEllipse(info)

    def drawFamilyHull(self):
        family_candidates = self.model.provideFamilyCandidateByColumn("Type")
        # TODO(team): implement the actual selection logic.
        selected_family = family_candidates[0]
        items = self.model.getItemsByFamily("Type", selected_family).values()
        self.drawHull(items)

    def drawAllHull(self):
        items = self.model.getAllItems().values()
        self.drawHull(items)

    def updateObjectsByAxis(self, x_column, y_column):
        #TODO(tienan): implement this.
        #Adjust the transformer to allow the flexibility of different x,y seleciton.
        pass

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

        #TODO(team): handle text in log scale. QFont cannot support pointSize < 1, which is alredy too large for our log object.
        text = self.scene.addText(mat_item.label if not self.config.log_scale else "",
                                  QFont("Arial", 12, 2))
        text.setPos(self.transformer.matCenterPoint(mat_item))
        text.setRotation(self.transformer.matRotation(mat_item))
        self.view.graphicItems.extend((elps, text))

    def drawHull(self, items: List[MaterialItem]):
        if len(items) > 0:
            r, g, b = self.model.getMeanColor(items)
            self.pen = QPen(QColor(125, 125, 125, 50), 0)
            self.brush = QBrush(QColor(r, g, b, 100))
            poly = self.scene.addPolygon(self.transformer.getEllipseHull(items), self.pen, self.brush)
            poly.setZValue(-1)
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
