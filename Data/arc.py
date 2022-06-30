#!/usr/bin/env python
# -*- coding: utf-8 -*-

from Data.bbox import BBox

class Arc(object):
    def __init__(self, center, radius, start_angle, end_angle):
        self.center = center
        self.radius = radius
        self.start_angle = start_angle
        self.end_angle = end_angle

        self.bbox = BBox()
        self.update()
        return

    # FIXME: see as circle for now
    def updateBBox(self):
        x_min = self.center.x - self.radius
        y_min = self.center.y - self.radius
        z_min = self.center.z - self.radius
        x_max = self.center.x + self.radius
        y_max = self.center.y + self.radius
        z_max = self.center.z + self.radius

        if not self.bbox.updateBBox(x_min, y_min, z_min, x_max, y_max, z_max):
            print("[ERROR][Arc::updateBBox]")
            print("\t updateBBox failed!")
        return True

    def update(self):
        if not self.updateBBox():
            print("[ERROR][Arc::update]")
            print("\t updateBBox failed!")
            return False
        return True

