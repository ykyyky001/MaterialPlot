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
TICKMARK_BAR_WIDTH = TICKMARK_BAR_HEIGHT
TICKMARK_HEIGHT = 8

MAJORTICK_HEIGHT = 19.0
MINORTICK_HEIGHT = 10.0

MINOR_TICK_COUNT = 10

# units of linearscale corresponding to logscale
LOGSCALE_UNITS = 1000.0
LINEARSCALE_UNITS = 1000.0
LINEAR_TO_LOG = LINEARSCALE_UNITS / LOGSCALE_UNITS

# 轨道的边框颜色:
TRACK_BORDER_COLOR = QColor("#202020")


class MarkLine(QGraphicsObject):
    """docstring for MarkLine: 刻度线."""
    TEXTANGLE = 0
    MAJORTICK_COLOR = QColor(112, 112, 112, 255)
    MINORTICK_COLOR = QColor(112, 112, 112, 102)

    def __init__(self, view):
        super(MarkLine, self).__init__()
        self.view = view
        self.view_scale = 100.0  # 画布缩放倍率
        self.textitem = None
        self._axisMode = MARKTRACK_MODE_LOGSCALE
        self._markTextItem = []
        self._markLines = []
        self._markLinesBold = []
        self._viewRect = None

        # 设置刻度线的颜色:
        self.pen = QPen(QColor(0, 0, 0, 0))
        self.pen.setWidth(0)  # linewidth not zooming
        self.brush = QBrush(MARKTRACK_BG_COLOR, Qt.SolidPattern)

        self.setZValue(200)
        self.setFlags(QGraphicsItem.ItemSendsScenePositionChanges)

    @property
    def axisMin(self):
        rect = self.view.getViewRect()
        return rect.left()

    @property
    def axisMax(self):
        rect = self.view.getViewRect()
        return rect.right()

    def makeMajorLine(self, a):
        rect = self.view.getViewRect()
        return QLineF(a, rect.bottom() - (TICKMARK_BAR_HEIGHT - MAJORTICK_HEIGHT) / self.view_scale, a,
                      rect.bottom() - TICKMARK_BAR_HEIGHT / self.view_scale)

    def transFormLogMinorCoord(self, a, basea=None, base=None):
        if self._axisMode == MARKTRACK_MODE_LOGSCALE and basea is not None:
            a = math.log10(a + 1) * base + basea
        return a
    def makeMinorLine(self, a, basea=None, base=None):
        rect = self.view.getViewRect()

        a = self.transFormLogMinorCoord(a, basea, base)

        return QLineF(a, rect.bottom() - (TICKMARK_BAR_HEIGHT - MINORTICK_HEIGHT) / self.view_scale, a,
                      rect.bottom() - TICKMARK_BAR_HEIGHT / self.view_scale)

    def makeTextPos(self, a):
        rect = self.view.getViewRect()
        y = rect.bottom() - 30 / self.view_scale
        return QPointF(a, y)

    def getFloorLogTick(self, v, index=0):
        if index == 0:
            tickindex = math.floor(v / LINEAR_TO_LOG)
            return 10 ** tickindex
        else:
            pass
    def getCeilLogTick(self, v, index=0):
        if index == 0:
            tickindex = math.ceil(v / LINEAR_TO_LOG)
            return 10 ** index

    def logUpdateMark(self):
        # hide all textitem first
        for item in self._markTextItem:
            item.hide()

        lines = []
        minor_lines = []
        self._markLinesBold = lines
        self._markLines = minor_lines
        arange = self.axisMax - self.axisMin
        if arange > LINEAR_TO_LOG * 5:
            self.linearUpdateMark()
        else:
            return
        i = 0

    def linearUpdateMark(self):
        arange = self.axisMax - self.axisMin
        divs = int(arange / 10 ** math.floor(math.log10(arange)))
        # divs: how many major ticks in view
        if divs < 2:
            divs *= 10
            base = 10 ** (math.floor(math.log10(arange)) - 1)
        else:
            base = 10 ** (math.floor(math.log10(arange)))
        # base: 0.1 1 10 100, etc
        lines = []
        minor_lines = []
        i = 0
        # hide all textitem first
        for item in self._markTextItem:
            item.hide()
        a = math.floor(self.axisMin / base) * base
        while a < self.axisMax:
            i += 1
            # calc major ticks
            lines.append(self.makeMajorLine(a))
            # calc minor ticks
            if self._axisMode == MARKTRACK_MODE_LINEAR:
                for j in range(1, MINOR_TICK_COUNT):
                    mina = a + j * base / MINOR_TICK_COUNT
                    minor_lines.append(self.makeMinorLine(mina))
            else:
                for j in range(1, MINOR_TICK_COUNT - 1):
                    minor_lines.append(self.makeMinorLine(j, a, base))
            # add tick texts
            if i >= len(self._markTextItem):
                item = QGraphicsTextItem(self)
                item.setFont(TICKS_TEXT_FONT)
                item.setDefaultTextColor(TICKS_TEXT_COLOR)
                item.setZValue(0)
                item.setRotation(self.TEXTANGLE)
                item.setFlag(QGraphicsItem.ItemIgnoresTransformations)
                self._markTextItem.append(item)
            else:
                item = self._markTextItem[i]
            item.setPos(self.makeTextPos(a))
            item.setPlainText(self.getMarkText(a))
            item.show()

            a += base

        self._markLinesBold = lines
        self._markLines = minor_lines
    def updateMark(self, force=False):
        # 获取可视区域
        rect = self.view.getViewRect()
        if not force and self._viewRect == rect:
            return
        self._viewRect = rect
        try:
            if self._axisMode == MARKTRACK_MODE_LINEAR:
                self.linearUpdateMark()
            else:
                self.logUpdateMark()
        except OverflowError:
            pass
    @staticmethod
    def lin2log(v):
        return 10 ** (v / LINEAR_TO_LOG)

    def getVisualCoord(self, logiccoord):
        if self._axisMode == MARKTRACK_MODE_LINEAR:
            return logiccoord
        else:
            return self.lin2log(logiccoord)

    def getMarkText(self, a):
        return "%g" % self.getVisualCoord(a)

    def setAxisMode(self, mode):
        self._axisMode = mode
        self.updateMark(force=True)
        self.update()

    def paintBackground(self, painter):
        # 背景色
        # self.
        rect = self.boundingRect()
        painter.pen().setWidth(0)
        painter.fillRect(rect, self.brush)

    def paintMinorTick(self, painter):
        # 细刻度线
        pen = QPen(self.MINORTICK_COLOR)
        pen.setWidth(0)
        painter.setPen(pen)
        painter.drawLines(self._markLines)

    def paintMajorTick(self, painter):
        # 粗刻度线
        boldPen = QPen(self.MAJORTICK_COLOR)
        boldPen.setWidth(0)
        painter.setPen(boldPen)
        painter.drawLines(self._markLinesBold)

    def paintBorderLine(self, painter):
        boldPen = QPen(self.MAJORTICK_COLOR)
        boldPen.setWidth(0)
        painter.setPen(boldPen)
        rect = self.boundingRect()
        # 水平线
        painter.drawLine(self.getBorderLine(rect))

    def paint(self, painter, option, widget):
        """绘制刻度线."""
        self.updateMark()

        self.paintBackground(painter)

        self.paintMinorTick(painter)

        self.paintMajorTick(painter)

        self.paintBorderLine(painter)

    def getBorderLine(self, rect):
        y = float(rect.bottom()) - TICKMARK_BAR_HEIGHT / self.view_scale
        return QLineF(rect.left(), y, rect.right(), y)

    def boundingRect(self):
        """交互范围."""
        rect = self.view.getViewRect()
        height = TICKMARK_BAR_HEIGHT / self.view_scale
        newRect = QRectF(rect.left(), rect.bottom() - height, rect.width(), height)
        return newRect

    def getViewScale(self):
        if self.scene() is None:
            return 1.0
        return self.view.getScale()

    def setViewScale(self, scale):
        self.view_scale = scale
        self.updateMark()
        self.update()


class VerticalMarkLine(MarkLine):
    TEXTANGLE = 90

    def boundingRect(self):
        """交互范围."""
        rect = self.view.getViewRect()
        width = TICKMARK_BAR_WIDTH / self.view_scale
        newRect = QRectF(rect.left(), rect.top(), width, rect.height())
        return newRect
    def transFormLogMinorCoord(self, a, basea=None, base=None):
        if self._axisMode == MARKTRACK_MODE_LOGSCALE and basea is not None:
            a = (1 - math.log10(a + 1)) * base + basea
        return a
    def getBorderLine(self, rect):
        x = float(rect.left()) + TICKMARK_BAR_WIDTH / self.view_scale
        return QLineF(x, rect.top(), x, rect.bottom())

    def getMarkText(self, a):
        return "%g" % self.getVisualCoord(-a)

    @property
    def axisMin(self):
        rect = self.view.getViewRect()
        return rect.top()

    @property
    def axisMax(self):
        rect = self.view.getViewRect()
        return rect.bottom()

    def makeMajorLine(self, a):
        rect = self.view.getViewRect()
        return QLineF(rect.left() + (TICKMARK_BAR_HEIGHT - MAJORTICK_HEIGHT) / self.view_scale, a,
                      rect.left() + TICKMARK_BAR_HEIGHT / self.view_scale, a)

    def makeMinorLine(self, a, basea=None, base=None):
        rect = self.view.getViewRect()

        a = self.transFormLogMinorCoord(a, basea, base)
        return QLineF(rect.left() + (TICKMARK_BAR_HEIGHT - MINORTICK_HEIGHT) / self.view_scale, a,
                      rect.left() + TICKMARK_BAR_HEIGHT / self.view_scale, a)

    def makeTextPos(self, a):
        rect = self.view.getViewRect()
        x = rect.left() + 30 / self.view_scale
        return QPointF(x, a)


class HShadowMarkLine(MarkLine):
    MAJORTICK_COLOR = QColor(112, 112, 112, 128)

    def __init__(self, view):
        super(HShadowMarkLine, self).__init__(view)
        self.setZValue(-200)

    def paint(self, painter, option, widget):
        """绘制刻度线."""
        self.updateMark()

        self.paintMajorTick(painter)

    def paintMajorTick(self, painter):
        # 粗刻度线
        boldPen = QPen(self.MAJORTICK_COLOR, 0, Qt.DotLine)
        # boldPen.setWidth(0)
        painter.setPen(boldPen)
        painter.drawLines(self._markLinesBold)

    def makeMajorLine(self, a):
        rect = self.view.getViewRect()
        return QLineF(a, rect.top(), a, rect.bottom())


class VShadowMarkLine(HShadowMarkLine):
    @property
    def axisMin(self):
        rect = self.view.getViewRect()
        return rect.top()

    @property
    def axisMax(self):
        rect = self.view.getViewRect()
        return rect.bottom()

    def makeMajorLine(self, a):
        rect = self.view.getViewRect()
        return QLineF(rect.left(), a, rect.right(), a)
