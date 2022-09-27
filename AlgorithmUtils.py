import numpy as np
from typing import List
from scipy.spatial import ConvexHull
from DataModel import MaterialItem


def ellipseHull(ellipses: List[MaterialItem], sf=0.01):
    pts = []
    for i, ellipse in enumerate(ellipses):
        t = np.linspace(0, 2*np.math.pi, 200)
        
        x = ellipse.w*(np.sin(t)+1)/2 + ellipse.x
        y = ellipse.h*(np.cos(t)+1)/2 + ellipse.y
        xy = np.stack((x, y)).T
        if ellipse.rotation is not None:
            # TODO(cow) rotation points
            pass
        pts.append(xy)

    pts = np.concatenate(pts, axis=0)
    hull = ConvexHull(pts)
    
    return pts[hull.vertices]
