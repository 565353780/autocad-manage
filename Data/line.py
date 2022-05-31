#!/usr/bin/env python
# -*- coding: utf-8 -*-

class Line(object):
    def __init__(self, start_point, end_point):
        self.start_point = start_point
        self.end_point = end_point

        self.bbox = [0, 0, 0, 0, 0, 0]
        return

    def updateBBox(self):
        x_min = min(start_point.x, end_point.x)
        y_min = min(start_point.y, end_point.y)
        z_min = min(start_point.z, end_point.z)
        x_max = max(start_point.x, end_point.x)
        y_max = max(start_point.y, end_point.y)
        z_max = max(start_point.z, end_point.z)

        self.bbox = [x_min, y_min, z_min, x_max, y_max, z_max]
        return True

