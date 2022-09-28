# -*- coding:utf-8 -*-
# @ModuleName: AxisObjects

from PySide2.QtWidgets import QGraphicsObject, QGraphicsItem, QGraphicsTextItem
from PySide2.QtGui import QBrush, QPen, QColor, QFont, QPolygonF
from PySide2.QtCore import QLineF, QPointF, QRectF, Qt
import math

MARKTRACK_MODE_LINEAR = 0
MARKTRACK_MODE_LOGSCALE = 1


MARKTRACK_HEIGHT = 40  # 刻度条的高度

# 画布的宽度:
SCENE_WIDTH = 1013
SCENE_HEIGHT = 948
# 时间刻度条的背景色:
MARKTRACK_BG_COLOR = QColor(200, 200, 200, 200)
# 时间刻度线的颜色:
TICKS_COLOR = QColor(134, 134, 134, 255)
# 刻度文字的颜色:
TICKS_TEXT_COLOR = QColor(0, 0, 0, 255)
# 刻度文字的字体:
TICKS_TEXT_FONT = QFont("微软雅黑", 10)

# 刻度线距离scene绘图面板最上方的距离
TICKMARK_BAR_HEIGHT = 38.0
TICKMARK_HEIGHT = 8

MAJORTICK_HEIGHT = 19.0
MINORTICK_HEIGHT = 10.0

MINOR_TICK_COUNT = 5


# 轨道的边框颜色:
TRACK_BORDER_COLOR = QColor("#202020")


class MarkLine(QGraphicsObject):
    """docstring for MarkLine: 刻度线."""

    def __init__(self, view):
        super(MarkLine, self).__init__()
        self.view = view
        self.startX = 0.0
        self.endX = SCENE_WIDTH
        self.view_scale = 1.0  # 画布缩放倍率
        self.textitem = None
        self._axisMode = MARKTRACK_MODE_LINEAR
        self._markTextItem = []
        self._markLines = []
        self._markLinesBold = []
        self._viewRect = None

        # 设置刻度线的颜色:
        self.pen = QPen(QColor(0,0,0,0))
        self.pen.setWidth(0)  # linewidth not zooming
        self.brush = QBrush(MARKTRACK_BG_COLOR, Qt.SolidPattern)

        self.setZValue(200)
        self.setFlags(QGraphicsItem.ItemSendsScenePositionChanges)

    def updateMark(self, force=False):
        # 获取可视区域
        rect = self.view.getViewRect()
        if not force and self._viewRect == rect:
            return
        self._viewRect = rect
        width = rect.width()
        divs = int(width / 10 ** math.floor(math.log10(width)))
        # divs: how many major ticks in view
        if divs < 2:
            divs *= 10
            base = 10 ** (math.floor(math.log10(width))-1)
        else:
            base = 10 ** (math.floor(math.log10(width)))
        # base: 0.1 1 10 100, etc
        lines = []
        minor_lines = []
        i = 0
        # hide all textitem first
        for item in self._markTextItem:
            item.hide()
        x = math.floor(rect.left() / base) * base
        while x < rect.right():
            i += 1
            # calc major ticks
            lines.append(QLineF(x, rect.bottom()-(TICKMARK_BAR_HEIGHT - MAJORTICK_HEIGHT)/self.view_scale, x, rect.bottom()-TICKMARK_BAR_HEIGHT/self.view_scale))
            # calc minor ticks
            for j in range(1, MINOR_TICK_COUNT):
                minx = x + j * base / MINOR_TICK_COUNT
                minor_lines.append(QLineF(minx, rect.bottom()-(TICKMARK_BAR_HEIGHT - MINORTICK_HEIGHT)/self.view_scale, minx, rect.bottom()-TICKMARK_BAR_HEIGHT/self.view_scale))

            # add tick texts
            if i >= len(self._markTextItem):
                item = QGraphicsTextItem(self)
                item.setFont(TICKS_TEXT_FONT)
                item.setDefaultTextColor(TICKS_TEXT_COLOR)
                item.setZValue(0)
                item.setFlag(QGraphicsItem.ItemIgnoresTransformations)
                self._markTextItem.append(item)
            else:
                item = self._markTextItem[i]
            y = rect.bottom() - 30 / self.view_scale
            item.setPos(QPointF(x, y))
            item.setPlainText("%g" % x)
            item.show()

            x += base

        self._markLinesBold = lines
        self._markLines = minor_lines

    def setAxisMode(self, mode):
        self._axisMode = mode
        self.updateMark(force=True)
        self.update()


    def paint(self, painter, option, widget):
        """绘制刻度线."""
        self.updateMark()
        # 背景色
        # self.
        rect = self.boundingRect()
        painter.pen().setWidth(0)
        painter.fillRect(rect, self.brush)

        # 细刻度线
        pen = QPen(QColor(112, 112, 112, 102))
        pen.setWidth(0)
        painter.setPen(pen)
        painter.drawLines(self._markLines)

        # 粗刻度线
        boldPen = QPen(QColor(112, 112, 112, 255))
        boldPen.setWidth(0)
        painter.setPen(boldPen)
        painter.drawLines(self._markLinesBold)

        # 水平线
        painter.setPen(boldPen)
        painter.drawLine(QLineF(rect.left(), rect.bottom()-TICKMARK_BAR_HEIGHT/self.view_scale, rect.right(), rect.bottom()-TICKMARK_BAR_HEIGHT/self.view_scale))

    def boundingRect(self):
        """交互范围."""
        rect = self.view.getViewRect()
        height = TICKMARK_BAR_HEIGHT/self.view_scale
        newRect = QRectF(rect.left(), rect.bottom() - height, rect.width(), height)
        return newRect

    def getViewScale(self):
        if self.scene() is None:
            return 1.0
        return self.view.getScale()

    def update(self, rect = None):
        if self.textitem:
            self.textitem.hide()
        super(MarkLine, self).update()
        if self.textitem:
            self.textitem.show()

    def setViewScale(self, scale):
        self.view_scale = scale
        self.updateMark()
        self.update()

