#!/usr/bin/env python
# -*- coding: utf-8 -*-

from autocad_manage.Data.base_shape import BaseShape
from autocad_manage.Data.bbox import BBox

class Arc(BaseShape):
    def __init__(self, center, radius, start_angle, end_angle, flatten_point_list):
        super(Arc, self).__init__()
        self.center = center
        self.radius = radius
        self.start_angle = start_angle
        self.end_angle = end_angle
        self.flatten_point_list = flatten_point_list

        self.type = "ARC"

        self.bbox = BBox()
        self.update()
        return

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
        print(line_start + "[Arc]")
        print(line_start + "\t center:")
        self.center.outputInfo(info_level + 1)
        print(line_start + "\t radius =", self.radius)
        print(line_start + "\t angle = [" + \
              str(self.start_angle) + "," + \
              str(self.end_angle) + "]")
        print(line_start + "\t start_point:")
        self.flatten_point_list[0].outputInfo(info_level + 1)
        print(line_start + "\t end_point:")
        self.flatten_point_list[-1].outputInfo(info_level + 1)
        return True

