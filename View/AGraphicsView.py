# -*- coding:utf-8 -*-
import PySide2.QtGui
from PySide2.QtWidgets import QGraphicsScene, QGraphicsView
from PySide2.QtCore import QPointF, QRectF, Qt
from PySide2.QtGui import QTransform
from .AxisObjects import MarkLine, VerticalMarkLine, VShadowMarkLine, HShadowMarkLine
import math


class AGraphicsView(QGraphicsView):
    def __init__(self, parent):
        super(AGraphicsView, self).__init__(parent)
        # initialize
        self.viewScale = 1.0
        self.scaleValue = 0
        self.rightDrag = False

        self.viewPosInScene = self.initPos
        self.lastViewPosInScene = self.initPos
        self.lastPos = QPointF(0, 0)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self._hMarkline = self._vMarkline = self._hsMarkline = self._vsMarkline = None

    def initHelperItems(self):
        self._hMarkline = MarkLine(self)
        self._vMarkline = VerticalMarkLine(self)
        self._hsMarkline = HShadowMarkLine(self)
        self._vsMarkline = VShadowMarkLine(self)
        self.scene().addItem(self._hMarkline)
        self.scene().addItem(self._vMarkline)
        self.scene().addItem(self._hsMarkline)
        self.scene().addItem(self._vsMarkline)

    @property
    def initPos(self):
        return QPointF(1013 * 0.5, 948 * 0.5)

    def mousePressEvent(self, mouseEvent):
        if mouseEvent.button() == Qt.LeftButton:
           pass
        elif mouseEvent.button() == Qt.MiddleButton:
            pass
        elif mouseEvent.button() == Qt.RightButton:
            self.setDragMode(QGraphicsView.ScrollHandDrag)
            self.lastPos = mouseEvent.pos()
            self.rightDrag = False

        return super(AGraphicsView, self).mousePressEvent(mouseEvent)

    def getViewRect(self):
        # todo: performance bottleneck
        return self.mapToScene(self.rect()).boundingRect()

    def mouseMoveEvent(self, mouseEvent):
        if self.dragMode() == QGraphicsView.ScrollHandDrag:
            self.rightDrag = True
            mousePos = QPointF(mouseEvent.pos())
            self.viewPosInScene = self.lastViewPosInScene + (QPointF(self.lastPos) - mousePos) / self.viewScale

            self.resetSceneRect()

        return super(AGraphicsView, self).mouseMoveEvent(mouseEvent)

    def mouseReleaseEvent(self, mouseEvent):
        self.setDragMode(QGraphicsView.NoDrag)
        self.lastViewPosInScene = self.viewPosInScene
        return super(AGraphicsView, self).mouseReleaseEvent(mouseEvent)

    def wheelEvent(self, mouseEvent: PySide2.QtGui.QWheelEvent):
        if self.dragMode() == QGraphicsView.ScrollHandDrag:
            return
        angleDelta = mouseEvent.angleDelta()
        delta = angleDelta.x() + angleDelta.y()
        self.scaleValue += delta * 0.002
        self.scaleValue = max(- 25, min(10.0, self.scaleValue))

        oldScale = self.viewScale
        self.viewScale = math.exp(self.scaleValue)
        # if self.scene():  # 通知scene
        #     self.scene().onViewScale(self.viewScale)
        scale = self.viewScale / oldScale

        mousePos =self.mapToScene(mouseEvent.pos())
        vec = QPointF(self.viewPosInScene - mousePos)
        self.lastViewPosInScene = self.viewPosInScene = mousePos + vec / scale
        self.resetSceneRect()

        # 刷新显示区域
        self._hMarkline.setViewScale(self.viewScale)
        self._vMarkline.setViewScale(self.viewScale)
        self._hsMarkline.setViewScale(self.viewScale)
        self._vsMarkline.setViewScale(self.viewScale)

        return super(AGraphicsView, self).wheelEvent(mouseEvent)

    def resetView(self):
        self.viewScale = 1.0
        self.scaleValue = 0
        self.viewPosInScene = self.initPos
        self.lastViewPosInScene = self.initPos
        self.lastPos = QPointF(0, 0)

        # 刷新显示区域
        if self._hMarkline:
            self._hMarkline.setViewScale(self.viewScale)
            self._vMarkline.setViewScale(self.viewScale)
            self._hsMarkline.setViewScale(self.viewScale)
            self._vsMarkline.setViewScale(self.viewScale)
        self.resetSceneRect()

    def resetSceneRect(self):
        rect = self.rect()
        width = rect.width() / self.viewScale

        height = rect.height() / self.viewScale

        rect = QRectF(self.viewPosInScene.x() - width / 2.0, self.viewPosInScene.y() - height / 2.0, width, height)
        # self.scene().setScale(self.viewScale)
        self.setSceneRect(rect)

        trans = QTransform()
        trans.scale(self.viewScale, self.viewScale)
        self.setTransform(trans)
        self.scene().update()
        if self._hMarkline:
            self._hMarkline.update()
            self._vMarkline.update()
            self._hsMarkline.update()
            self._vsMarkline.update()
