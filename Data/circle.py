#!/usr/bin/env python
# -*- coding: utf-8 -*-

from Data.bbox import BBox

class Circle(object):
    def __init__(self, center, radius):
        self.center = center
        self.radius = radius

        self.bbox = BBox()
        self.update()
        return

    def updateBBox(self):
        x_min = self.center.x - self.radius
        y_min = self.center.y - self.radius
        z_min = self.center.z - self.radius
        x_max = self.center.x + self.radius
        y_max = self.center.y + self.radius
        z_max = self.center.z + self.radius

        if not self.bbox.updateBBox(x_min, y_min, z_min, x_max, y_max, z_max):
            print("[ERROR][Circle::updateBBox]")
            print("\t updateBBox failed!")
            return False
        return True

    def update(self):
        if not self.updateBBox():
            print("[ERROR][Circle::update]")
            print("\t updateBBox failed!")
            return False
        return True

