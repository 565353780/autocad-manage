#!/usr/bin/env python
# -*- coding: utf-8 -*-

class Point(object):
    def __init__(self, x, y, z):
        self.x = x
        self.y = y
        self.z = z

        self.bbox = [0, 0, 0, 0, 0, 0]
        self.updateBBox()
        return

    def updateBBox(self):
        x_min = self.x
        y_min = self.y
        z_min = self.z
        x_max = self.x
        y_max = self.y
        z_max = self.z

        self.bbox = [x_min, y_min, z_min, x_max, y_max, z_max]
        return True

