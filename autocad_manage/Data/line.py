#!/usr/bin/env python
# -*- coding: utf-8 -*-

from math import sqrt, atan, pi

from autocad_manage.Data.base_shape import BaseShape
from autocad_manage.Data.point import Point
from autocad_manage.Data.bbox import BBox


class Line(BaseShape):

    def __init__(self, start_point=Point(), end_point=Point()):
        super(Line, self).__init__()
        self.start_point = start_point
        self.end_point = end_point

        self.type = "LINE"

        self.diff_point = None
        self.bbox = BBox()
        self.k = None
        self.update()
        return

    def updateDiffPoint(self):
        x_diff = self.end_point.x - self.start_point.x
        y_diff = self.end_point.y - self.start_point.y
        z_diff = self.end_point.z - self.start_point.z
        self.diff_point = Point(x_diff, y_diff, z_diff)
        return True

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
            return False
        return True

    def updateK(self):
        if self.diff_point.x == 0:
            if self.diff_point.y == 0:
                self.k = None
                return True

            self.k = float("inf")
            return True

        self.k = self.diff_point.y / self.diff_point.x
        return True

    def update(self):
        if not self.updateDiffPoint():
            print("[ERROR][Line::update]")
            print("\t updateDiffPoint failed!")
            return False
        if not self.updateBBox():
            print("[ERROR][Line::update]")
            print("\t updateBBox failed!")
            return False
        if not self.updateK():
            print("[ERROR][Line::update]")
            print("\t updateK failed!")
            return False
        return True

    def getLength(self):
        x_diff = self.end_point.x - self.start_point.x
        y_diff = self.end_point.y - self.start_point.y
        length2 = x_diff * x_diff + y_diff * y_diff
        return sqrt(length2)

    def getRad(self):
        if self.k is None:
            return None

        rad = atan(self.k)
        return rad

    def getAngle(self):
        if self.k is None:
            return None

        rad = atan(self.k)
        angle = rad * 180.0 / pi
        return angle

    def isPoint(self):
        if self.bbox.diff_point.x == 0 and self.bbox.diff_point.y == 0:
            return True
        return False

    def getMiddlePoint(self):
        x_mean = (self.start_point.x + self.end_point.x) / 2.0
        y_mean = (self.start_point.y + self.end_point.y) / 2.0
        z_mean = (self.start_point.z + self.end_point.z) / 2.0
        middle_point = Point(x_mean, y_mean, z_mean)
        return middle_point

    def outputInfo(self, info_level=0):
        line_start = "\t" * info_level
        print(line_start + "[Line]")
        print(line_start + "\t start_point:")
        self.start_point.outputInfo(info_level + 1)
        print(line_start + "\t end_point:")
        self.end_point.outputInfo(info_level + 1)
        print(line_start + "\t diff_point :")
        self.diff_point.outputInfo(info_level + 1)
        print(line_start + "\t k =", self.k)
        return True
