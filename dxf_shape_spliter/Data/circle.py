#!/usr/bin/env python
# -*- coding: utf-8 -*-

from dxf_shape_spliter.Data.label import Label
from dxf_shape_spliter.Data.bbox import BBox

class Circle(Label):
    def __init__(self, center, radius):
        super(Circle, self).__init__()
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

    def setNewLabel(self, new_label):
        self.label = new_label
        return True

    def addLabel(self, new_label):
        if self.label == "Unknown":
            self.label = new_label
            return True

        if new_label in self.label:
            return True

        self.label += "_" + new_label
        return True

    def outputInfo(self, info_level=0):
        line_start = "\t" * info_level
        print(line_start + "[Circle]")
        print(line_start + "\t center:")
        self.center.outputInfo(info_level + 1)
        print(line_start + "\t radius =", self.radius)
        return True

