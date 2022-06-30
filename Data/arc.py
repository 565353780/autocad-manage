#!/usr/bin/env python
# -*- coding: utf-8 -*-

from Data.label import Label
from Data.point import Point
from Data.bbox import BBox

class Arc(Label):
    def __init__(self, center, radius, start_angle, end_angle, flatten_point_list):
        super(Arc, self).__init__()
        self.center = center
        self.radius = radius
        self.start_angle = start_angle
        self.end_angle = end_angle
        self.flatten_point_list = [Point(point[0], point[1], point[2]) for point in flatten_point_list]

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

