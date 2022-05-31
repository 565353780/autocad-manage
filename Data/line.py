#!/usr/bin/env python
# -*- coding: utf-8 -*-

from Data.point import Point
from Data.bbox import BBox

class Line(object):
    def __init__(self, start_point=Point(), end_point=Point()):
        self.start_point = start_point
        self.end_point = end_point

        self.bbox = BBox()
        self.updateBBox()
        return

    def updateBBox(self):
        x_min = min(self.start_point.x, self.end_point.x)
        y_min = min(self.start_point.y, self.end_point.y)
        z_min = min(self.start_point.z, self.end_point.z)
        x_max = max(self.start_point.x, self.end_point.x)
        y_max = max(self.start_point.y, self.end_point.y)
        z_max = max(self.start_point.z, self.end_point.z)

        if not self.bbox.updateBBox(x_min, y_min, z_min, x_max, y_max, z_max):
            print("[ERROR][Line::updateBBox]")
            print("\t updateBBox failed!")
        return True

