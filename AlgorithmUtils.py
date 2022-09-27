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

if "__main__" == __name__:
    import csv
    currentData = []
    with open('test.csv', "r") as f:
        csvrows = csv.DictReader(f)
        for index, row in enumerate(csvrows):
            currentData.append(row)
    ellipses = []
    for raw_data in currentData:
        eclipse_info = simpleEclipse(x = float(raw_data["Param2_mean"]),
                                    y = float(raw_data["Param3_mean"]),
                                    w = float(raw_data["Param2_sd"]),
                                    h = float(raw_data["Param3_sd"]),
                                    label = raw_data["Name"])
        ellipses.append(eclipse_info)
    ellipseHull(ellipses)