import numpy as np
from typing import List
from scipy.spatial import ConvexHull
from DataModel import MaterialItem

class simpleEllipse:
    def __init__(self, x, y, w, h, rotation):
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        self.rotation = rotation

    @staticmethod
    def initFromMatItem(item: MaterialItem):
        return simpleEllipse(item.x, item.y, item.w, item.h, item.rotation)


def ellipseHull(ellipses: List[simpleEllipse], expand_ratio, step):
    if len(ellipses) == 0:
        return None
    pts = []
    for i, ellipse in enumerate(ellipses):
        t = np.linspace(0, 2*np.math.pi, step)
        # Sample points along the surface of the ellipse.
        x = ellipse.w*np.sin(t)/2 * expand_ratio + ellipse.x
        y = ellipse.h*np.cos(t)/2 * expand_ratio + ellipse.y
        xy = np.stack((x, y)).T
        if ellipse.rotation is not None:
            # TODO(cow) rotation points
            pass
        pts.append(xy)
    pts = np.concatenate(pts, axis=0)
    hull = ConvexHull(pts)
    
    return pts[hull.vertices]
