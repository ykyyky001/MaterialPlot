# -*- coding:utf-8 -*-
from PySide2.QtCore import QRectF, QPointF
from PySide2.QtWidgets import QGraphicsScene
from PySide2.QtGui import QBrush, QPen, QColor, QFont
from DataModel import AshbyModel, MaterialItem


class AshbyGraphicsController(object):
    def __init__(self, scene: QGraphicsScene, model: AshbyModel):
        self.scene = scene
        self.pen = QPen(QColor(0,0,0))
        self.model = model
        self.graphicItems = [] # not necessary at present, for further use

    def clearScene(self):
        self.scene.clear()
        self.graphicItems.clear() # not necessary at present, for further use

    def drawAllMaterialEclipses(self):
        for name, info in self.model.getAllItems().items():
            self.drawEllipse(info)

    def drawEllipse(self, mat_item: MaterialItem):
        brush = QBrush(QColor(mat_item.color_r, mat_item.color_g, mat_item.color_b, a = 100))
        elps = self.scene.addEllipse(QRectF(mat_item.x, mat_item.y, mat_item.w, mat_item.h), self.pen, brush)
        text = self.scene.addText(mat_item.label, QFont("Arial", 12, 2))
        text.setPos(QPointF(mat_item.x, mat_item.y))
        elps.setRotation(mat_item.rotation)
        text.setRotation(mat_item.rotation)

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