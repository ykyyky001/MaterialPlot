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
        if divs < 2:
            divs *= 10
            base = 10 ** (math.floor(math.log10(width))-1)
        else:
            base = 10 ** (math.floor(math.log10(width)))

        lines = []
        minor_lines = []
        i = 0
        for item in self._markTextItem:
            item.hide()
        x = math.floor(rect.left() / base) * base
        while x < rect.right():
            i += 1
            lines.append(QLineF(x, rect.top()+(TICKMARK_BAR_HEIGHT - MAJORTICK_HEIGHT)/self.view_scale, x, rect.top()+TICKMARK_BAR_HEIGHT/self.view_scale))
            for j in range(1, MINOR_TICK_COUNT):
                minx = x + j * base / MINOR_TICK_COUNT
                minor_lines.append(QLineF(minx, rect.top()+(TICKMARK_BAR_HEIGHT - MINORTICK_HEIGHT)/self.view_scale, minx, rect.top()+TICKMARK_BAR_HEIGHT/self.view_scale))
            if i >= len(self._markTextItem):
                item = QGraphicsTextItem(self)
                item.setFont(TICKS_TEXT_FONT)
                item.setDefaultTextColor(TICKS_TEXT_COLOR)
                item.setZValue(0)
                item.setFlag(QGraphicsItem.ItemIgnoresTransformations)
                self._markTextItem.append(item)
            else:
                item = self._markTextItem[i]
            y = rect.top() + 10 / self.view_scale
            item.setPos(QPointF(x, y))
            item.setPlainText("%g" % x)
            item.show()

            x += base

        self._markLinesBold = lines
        self._markLines = minor_lines

        return
        # 根据缩放，划定不同的刻度步长
        timelineTick = self.view.tick
        tickLength = timelineTick.getTickLength()
        maxTick = timelineTick.getEndTick()
        scale = self.getViewScale()
        if scale < 0.012:	scaleLevel = 32
        elif scale < 0.025:	scaleLevel = 16
        elif scale < 0.05:	scaleLevel = 8
        elif scale < 0.1:	scaleLevel = 4
        elif scale < 0.2: 	scaleLevel = 2
        elif scale < 0.5: 	scaleLevel = 1
        elif scale < 0.8: 	scaleLevel = 0.5
        elif scale < 1.5:	scaleLevel = 0.25
        elif scale < 3:		scaleLevel = 0.125
        else:   			scaleLevel = 0.0625
        # 步长必须是tickLength的偶数倍
        markStep = timelineTick.align2tick(scaleLevel * MARKTRACK_TICK_LENGTH)
        if (markStep / tickLength) % 2 == 1:
            markStep += tickLength

        lines = []  # 细刻度线
        linesBold = []  # 粗刻度线
        marks = []  # 需要显示文字的位置
        left = max(timelineTick.pos2tick(rect.left()), timelineTick.getStartTick())
        right = min(timelineTick.pos2tick(rect.right()) + markStep, maxTick)
        markTick = max(int(left / markStep) * markStep, 0)  # 返回小于left的最大step倍数
        while markTick <= right:
            # 大刻度
            marks.append(markTick)
            x = timelineTick.tick2pos(markTick)
            y = rect.top() + TICKMARK_BAR_HEIGHT + self._viewRect.height()
            y2 = y - self._viewRect.height() - TICKMARK_HEIGHT
            linesBold.append(QLineF(x, y, x, y2))

            # 小刻度
            if scale < 2:
                # 未防止太过密集，直接划分成4份
                mini_step = markStep / 4
                y2 = y - self._viewRect.height() - TICKMARK_HEIGHT / 4
                for i in range(1, 4):
                    # 小刻度也必须对齐tickLength
                    mini_markTick = timelineTick.align2tick(markTick + mini_step * i)
                    if mini_markTick > maxTick:
                        break
                    x = timelineTick.tick2pos(mini_markTick)
                    lines.append(QLineF(x, y, x, y2))

            elif scale < 4:
                # 放大时，直接在对应帧的位置处画刻度
                mini_step = tickLength
                y2 = y - self._viewRect.height() - TICKMARK_HEIGHT / 4
                while mini_step < markStep:
                    x = timelineTick.tick2pos(markTick + mini_step)
                    lines.append(QLineF(x, y, x, y2))
                    mini_step += tickLength

            else:
                # 缩放到最大时，每帧显示文字
                mini_step = tickLength
                y2 = y - self._viewRect.height() - TICKMARK_HEIGHT
                while mini_step < markStep and mini_step <= maxTick:
                    x = timelineTick.tick2pos(markTick + mini_step)
                    linesBold.append(QLineF(x, y, x, y2))
                    marks.append(markTick + mini_step)
                    mini_step += tickLength

            markTick += markStep
        self._markLines = lines
        self._markLinesBold = linesBold

        # 刻度文字
        if len(self._markTextItem) < len(marks):
            for i in range(len(marks) - len(self._markTextItem)):
                item = QGraphicsTextItem(self)
                item.setFont(TICKS_TEXT_FONT)
                item.setDefaultTextColor(TICKS_TEXT_COLOR)
                item.setZValue(0)
                item.setFlag(QGraphicsItem.ItemIgnoresTransformations)
                self._markTextItem.append(item)

        for item in self._markTextItem:
            item.hide()

        i = 0
        for markTick in marks:
            item = self._markTextItem[i]
            x = timelineTick.tick2pos(markTick)
            y = rect.top() + TICKMARK_BAR_HEIGHT - TICKMARK_HEIGHT - 12
            item.setPos(QPointF(x, y))

            text = self.view.tickToTagText(markTick)
            # text += "\n" + str(markTick)
            item.setPlainText(text)
            item.show()
            i += 1

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
        painter.drawLine(QLineF(rect.left(), rect.top()+TICKMARK_BAR_HEIGHT/self.view_scale, rect.right(), rect.top()+TICKMARK_BAR_HEIGHT/self.view_scale))

    def boundingRect(self):
        """交互范围."""
        rect = self.view.getViewRect()
        newRect = QRectF(rect.left(), rect.top(), rect.width(), TICKMARK_BAR_HEIGHT/self.view_scale)
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

