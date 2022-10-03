from math import log10
from typing import List

from PySide2.QtCore import QPointF, QRectF
from PySide2.QtGui import QPolygonF

from AlgorithmUtils import ellipseHull, simpleEllipse
from DataModel import MaterialItem

class GraphicConfig():
    '''
    Describe the plot features.
    '''

    def __init__(self):
        self.expend_ratio = 2.
        self.hull_sampling_step = 200
        self.log_scale = True

    def updateConfig(self, expend_ratio: float=None,
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

