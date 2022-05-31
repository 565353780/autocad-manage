#!/usr/bin/env python
# -*- coding: utf-8 -*-

class Circle(object):
    def __init__(self, center, radius):
        self.center = center
        self.radius = radius

        self.bbox = [0, 0, 0, 0, 0, 0]
        self.updateBBox()
        return

    def updateBBox(self):
        x_min = self.center.x - self.radius
        y_min = self.center.y - self.radius
        z_min = self.center.z - self.radius
        x_max = self.center.x + self.radius
        y_max = self.center.y + self.radius
        z_max = self.center.z + self.radius

        self.bbox = [x_min, y_min, z_min, x_max, y_max, z_max]
        return True

