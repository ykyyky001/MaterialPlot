# -*- coding:utf-8 -*-
import PySide2.QtGui
from PySide2.QtWidgets import QGraphicsScene, QGraphicsView, QGraphicsTextItem
from PySide2.QtCore import QPointF, QRectF, Qt
from PySide2.QtGui import QTransform
from .AxisObjects import MarkLine, VerticalMarkLine, VShadowMarkLine, HShadowMarkLine
import math

FIT_EXPAND_MARGIN_RATIO = 0.1


class AGraphicsView(QGraphicsView):
    def __init__(self, parent):
        super(AGraphicsView, self).__init__(parent)
        # initialize
        self.viewScale = 100.0
        self.scaleValue = math.log(self.viewScale)
        self.rightDrag = False

        self.viewPosInScene = self.initPos
        self.lastViewPosInScene = self.initPos
        self.lastPos = QPointF(0, 0)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self._hMarkline = self._vMarkline = self._hsMarkline = self._vsMarkline = None

        self.graphicItems = []

    def changeAxisMode(self, mode):
        if self._hMarkline:
            self._hMarkline.setAxisMode(mode)
            self._vMarkline.setAxisMode(mode)
            self._hsMarkline.setAxisMode(mode)
            self._vsMarkline.setAxisMode(mode)
            self.refreshMarks()

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
        return QPointF(0, 0)

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

        mousePos = self.mapToScene(mouseEvent.pos())
        vec = QPointF(self.viewPosInScene - mousePos)
        self.lastViewPosInScene = self.viewPosInScene = mousePos + vec / scale
        self.resetSceneRect()

        # 刷新显示区域
        self._hMarkline.setViewScale(self.viewScale)
        self._vMarkline.setViewScale(self.viewScale)
        self._hsMarkline.setViewScale(self.viewScale)
        self._vsMarkline.setViewScale(self.viewScale)

        return super(AGraphicsView, self).wheelEvent(mouseEvent)

    def fitView(self):
        if not self.graphicItems:
            self.resetView()
            return
        rect = QRectF()
        for item in self.graphicItems:
            bb = item.boundingRect()
            rect = rect.united(bb)
        if rect.left() < rect.top():
            rect.setTop(rect.left())
        else:
            rect.setLeft(rect.top())
        if rect.right() < rect.bottom():
            rect.setRight(rect.bottom())
        else:
            rect.setBottom(rect.right())
        widthmargin = rect.width() * FIT_EXPAND_MARGIN_RATIO
        rect.setWidth(rect.width() + widthmargin)
        rect.setHeight(rect.height() + widthmargin)
        rect.setTop(rect.top() - widthmargin * 0.8)
        rect.setLeft(rect.left() - widthmargin * 0.8)
        originrect = self.rect()
        self.viewScale = originrect.height() / rect.height()
        self.scaleValue = math.log(self.viewScale)
        self.viewPosInScene = self.lastViewPosInScene = QPointF((rect.left() + rect.right()) * 0.5,
                                                                (rect.top() + rect.bottom()) * 0.5)
        self.resetSceneRect()

    def resetView(self):
        self.viewScale = 100.0
        self.scaleValue = math.log(self.viewScale)
        self.viewPosInScene = self.initPos
        self.lastViewPosInScene = self.initPos
        self.lastPos = QPointF(0, 0)

        self.resetSceneRect()

    def refreshMarks(self):
        # 刷新显示区域
        if self._hMarkline:
            self._hMarkline.setViewScale(self.viewScale)
            self._vMarkline.setViewScale(self.viewScale)
            self._hsMarkline.setViewScale(self.viewScale)
            self._vsMarkline.setViewScale(self.viewScale)

            self._hMarkline.update()
            self._vMarkline.update()
            self._hsMarkline.update()
            self._vsMarkline.update()

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
        for item in self.graphicItems:
            if isinstance(item, QGraphicsTextItem):
                item.setScale(1.0 / self.viewScale)
        self.scene().update()
        self.refreshMarks()
