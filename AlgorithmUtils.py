import numpy as np
from typing import List
from scipy.spatial import ConvexHull
from DataModel import MaterialItem


def ellipseHull(ellipses: List[MaterialItem], sf=0.01):
    pts = []
    for i, ellipse in enumerate(ellipses):
        t = np.linspace(0, 2*np.math.pi, 200)
        
        x = ellipse.w*np.sin(t)/2 * 2 + ellipse.x + ellipse.w/2
        y = ellipse.h*np.cos(t)/2 * 2 + ellipse.y + ellipse.h/2
        xy = np.stack((x, y)).T
        if ellipse.rotation is not None:
            # TODO(cow) rotation points
            pass
        pts.append(xy)

    pts = np.concatenate(pts, axis=0)
    hull = ConvexHull(pts)
    
    return pts[hull.vertices]
