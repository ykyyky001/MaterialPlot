import numpy as np
from main import simpleEclipse
from typing import List
from scipy.spatial import ConvexHull

COLOR = ((0, 255, 0), (0, 0, 255), (255, 0, 0))
DEBUG = False

def EllipseHull(ellipses: List[simpleEclipse], sf=0.01):
    # TODO remove DEBUG code
    
    if DEBUG:
        import cv2
        img = np.zeros((1200, 400, 3))
        img[...] = 255
    pts = []
    for i, ellipse in enumerate(ellipses):
        t = np.linspace(0, 2*np.math.pi, 200)
        x = ellipse.w*np.sin(t) + ellipse.x
        y = ellipse.h*np.cos(t) + ellipse.y
        xy = np.stack((x, y)).T
        if DEBUG:
            xy[:, 0] /= 2
            xy[:, 0] += 100
            xy[:, 1] /= 2
            for pt in xy:
                img[int(pt[1]), int(pt[0]), :] = COLOR[i]
        pts.append(xy)

    pts = np.concatenate(pts, axis=0)
    hull = ConvexHull(pts)
    
    if DEBUG:
        for pt in pts[hull.vertices]:
            img[int(pt[1]), int(pt[0]), :] = (0, 127, 127)
        cv2.imshow('test1', img)

        cv2.waitKey(0)
    return hull

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
    EllipseHull(ellipses)