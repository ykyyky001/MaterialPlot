# -*- coding:utf-8 -*-
from math import log
from typing import List

from PySide2.QtCore import QRectF, QPointF
from PySide2.QtWidgets import QGraphicsScene
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
        self.log_scale = False

    def update_config(self, expend_ratio: float, hull_sampling_step, int, log_scale: bool):
        self.expend_ratio = expend_ratio
        self.hull_sampling_step = hull_sampling_step
        self.log_scale = log_scale

class GraphicTransformer():
    '''
    Converts the coordinate-related features to the appropriate plot scale based on the config.
    '''
    def __init__(self, config: GraphicConfig):
        self.config = config

    def matToSquare(self, mat_item: MaterialItem):
        if self.config.log_scale:
            # TODO(team): implement this.
            pass
        else:
            return QRectF(mat_item.x - mat_item.w / 2.,
                          mat_item.y - mat_item.h / 2.,
                          mat_item.w, mat_item.h)

    def matUpperLeftPoint(self, mat_item: MaterialItem):
        if self.config.log_scale:
            # TODO(team): implement this.
            pass
        else:
            return QPointF(mat_item.x - mat_item.w / 2., mat_item.y  - mat_item.h / 2.)

    def matCenterPoint(self, mat_item: MaterialItem):
        if self.config.log_scale:
            # TODO(team): implement this.
            pass
        else:
            return QPointF(mat_item.x, mat_item.y)

    # TODO(team): implement this
    def matRotation(self, mat_item: MaterialItem):
        if self.config.log_scale:
            pass
        else:
            return mat_item.rotation

    def getEllipseHull(self, items: List[MaterialItem]):
        return ellipseHull([self.matToSimpleEllipse(item) for item in items],
                            self.config.expend_ratio,
                            self.config.hull_sampling_step)

    def matToSimpleEllipse(self, item: MaterialItem):
        if self.config.log_scale:
            # TODO(team): implement this
            pass
        else:
            elps = simpleEllipse()
            elps.initFromMatItem(item)
        return elps

class AshbyGraphicsController(object):
    def __init__(self, scene: QGraphicsScene, filename: str):
        self.scene = scene
        self.pen = QPen(QColor(0,0,0))
        self.pen.setWidth(0)
        self.model = AshbyModel(filename)
        self.config = GraphicConfig()
        self.transformer = GraphicTransformer(self.config)
        self.graphicItems = []

    #
    # Public
    #
    # TODO(team): add UI to call this for online update.
    def update_config(self, expend_ratio: float, hull_sampling_step: int, log_scale: bool):
        self.config.update_config(expend_ratio, hull_sampling_step, log_scale)
        self.transformer = GraphicTransformer(self.config)
        self.clearScene()

    def clearScene(self):
        for item in self.graphicItems:
            self.scene.removeItem(item)
        # self.scene.clear()
        self.graphicItems.clear()

    def drawAllMaterialEclipses(self):
        for name, info in self.model.getAllItems().items():
            self.drawEllipse(info)

    def drawFamilyHull(self):
        candidate_columns = self.model.getCandidateColumns()
        #TODO(team): implement the actual selection logic.
        selected_column = candidate_columns[0]
        family_candidates = self.model.provideFamilyCandidateByColumn(selected_column)
        #TODO(team): implement the actual selection logic.
        selected_family = family_candidates[0]
        items = self.model.getItemsByFamily(selected_column, selected_family).values()
        self.drawHull(items)

    def drawAllHull(self):
        items = self.model.getAllItems().values()
        self.drawHull(items)

    #
    # Private
    #
    def drawEllipse(self, mat_item: MaterialItem):
        brush = QBrush(QColor(mat_item.color_r, mat_item.color_g, mat_item.color_b, a = 255))
        elps = self.scene.addEllipse(self.transformer.matToSquare(mat_item), self.pen, brush)
        text = self.scene.addText(mat_item.label, QFont("Arial", 12, 2))
        text.setPos(self.transformer.matCenterPoint(mat_item))
        elps.setRotation(self.transformer.matRotation(mat_item))
        text.setRotation(self.transformer.matRotation(mat_item))
        self.graphicItems.extend((elps, text))

    def drawHull(self, items: List[MaterialItem]):
        if len(items) > 0:
            r, g, b = self.model.getMeanColor(items)
            hull_v = self.transformer.getEllipseHull(items)
            # i add the QLineEdit in UI called Exp_Ratio. How to call it here?
            polygon = QPolygonF(list(map(QPointF, *hull_v.T)))
            self.pen = QPen(QColor(125, 125, 125, 50))
            self.brush = QBrush(QColor(r, g, b, 100))
            poly = self.scene.addPolygon(polygon, self.pen, self.brush)
            self.graphicItems.append(poly)

    def drawLine(self):
        # fake example, make your draw with your data
        self.scene.addLine(0, 0, 100, 400, self.pen)
        for i in range(self.model.getCount()):
            matitem = self.model.getItem(i)
            mean = matitem.getMean("Param3")
            std = matitem.getStd("Param3")
            # draw a cross
            graphicitem = self.scene.addLine(mean -10 , std - 10, mean + 10, std+10, self.pen)
            graphicitem2 = self.scene.addLine(mean -10 , std + 10, mean + 10, std-10, self.pen)

            self.graphicItems.append(graphicitem)	# not necessary at present, for further use
            self.graphicItems.append(graphicitem2)	# not necessary at present, for further use


