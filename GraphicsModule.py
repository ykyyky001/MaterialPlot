# -*- coding:utf-8 -*-
from typing import List
from PySide2.QtCore import QRectF, QPointF
from PySide2.QtWidgets import QGraphicsScene
from PySide2.QtGui import QBrush, QPen, QColor, QFont, QPolygonF
from PySide2.QtCore import QPointF
from DataModel import AshbyModel, MaterialItem
from AlgorithmUtils import ellipseHull


class AshbyGraphicsController(object):
    def __init__(self, scene: QGraphicsScene, filename: str):
        self.scene = scene
        self.pen = QPen(QColor(0,0,0))
        self.pen.setWidth(0)
        self.model = AshbyModel(filename)
        self.graphicItems = []

    #
    # Public
    #
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
        #TODO(tienan): implement the actual pop-up selection logic.
        selected_column = candidate_columns[0]
        family_candidates = self.model.provideFamilyCandidateByColumn(selected_column)
        #TODO(tienan): implement the actual pop-up selection logic.
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
        elps = self.scene.addEllipse(QRectF(mat_item.x, mat_item.y, mat_item.w, mat_item.h), self.pen, brush)
        text = self.scene.addText(mat_item.label, QFont("Arial", 12, 2))
        text.setPos(QPointF(mat_item.x, mat_item.y))
        elps.setRotation(mat_item.rotation)
        text.setRotation(mat_item.rotation)
        self.graphicItems.extend((elps, text))

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

    def drawHull(self, items: List[MaterialItem]):
        if len(items) > 0:
            r, g, b = self.model.getMeanColor(items)
            hull_v = ellipseHull(items, 2, 200) # expand ratio = 2, step = 200
            # i add the QLineEdit in UI called Exp_Ratio. How to call it here?
            polygon = QPolygonF(list(map(QPointF, *hull_v.T)))
            self.pen = QPen(QColor(125, 125, 125, 50))
            self.brush = QBrush(QColor(r, g, b, 100))
            poly = self.scene.addPolygon(polygon, self.pen, self.brush)
            self.graphicItems.append(poly)
