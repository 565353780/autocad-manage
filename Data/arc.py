#!/usr/bin/env python
# -*- coding: utf-8 -*-

from Data.point import Point
from Data.bbox import BBox

class Arc(object):
    def __init__(self, center, radius, start_angle, end_angle, flatten_point_list):
        self.center = center
        self.radius = radius
        self.start_angle = start_angle
        self.end_angle = end_angle
        self.flatten_point_list = [Point(point[0], point[1], point[2]) for point in flatten_point_list]

        self.bbox = BBox()
        self.update()
        return

    # FIXME: see as circle for now
    def updateBBox(self):
        for point in self.flatten_point_list:
            if not self.bbox.addPosition(point):
                print("[ERROR][Arc::updateBBox]")
                print("\t updateBBox failed!")
                return False
        return True

    def update(self):
        if not self.updateBBox():
            print("[ERROR][Arc::update]")
            print("\t updateBBox failed!")
            return False
        return True

