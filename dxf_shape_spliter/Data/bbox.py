#!/usr/bin/env python
# -*- coding: utf-8 -*-

from dxf_shape_spliter.Data.point import Point

class BBox(object):
    def __init__(self, min_point=Point(), max_point=Point()):
        self.min_point = min_point
        self.max_point = max_point

        self.diff_point = Point()

        self.update()
        if self.diff_point.isZero():
            self.reset()
        return

    def reset(self):
        inf = float("inf")
        self.min_point = Point(inf, inf, inf)
        self.max_point = Point(-inf, -inf, -inf)
        self.diff_point = Point()
        return True

    def updateDiffPoint(self):
        x_diff = self.max_point.x - self.min_point.x
        y_diff = self.max_point.y - self.min_point.y
        z_diff = self.max_point.z - self.min_point.z

        self.diff_point = Point(x_diff, y_diff, z_diff)
        return True

    def update(self):
        if not self.updateDiffPoint():
            print("[ERROR][BBox::update]")
            print("\t updateDiffPoint failed!")
            return False
        return True

    def addPosition(self, point):
        if self.min_point.x == float("inf"):
            self.min_point = point
            self.max_point = point
            self.updateDiffPoint()
            return True

        # TODO: Why this way wrong?
        #  self.min_point.x = min(self.min_point.x, point.x)
        #  self.min_point.y = min(self.min_point.y, point.y)
        #  self.min_point.z = min(self.min_point.z, point.z)
        #  self.max_point.x = max(self.max_point.x, point.x)
        #  self.max_point.y = max(self.max_point.y, point.y)
        #  self.max_point.z = max(self.max_point.z, point.z)

        # replace code to this paragraph
        x_min = min(self.min_point.x, point.x)
        y_min = min(self.min_point.y, point.y)
        z_min = min(self.min_point.z, point.z)
        x_max = max(self.max_point.x, point.x)
        y_max = max(self.max_point.y, point.y)
        z_max = max(self.max_point.z, point.z)
        self.min_point = Point(x_min, y_min, z_min)
        self.max_point = Point(x_max, y_max, z_max)

        self.updateDiffPoint()
        return True

    def addBBoxPosition(self, bbox):
        if not self.addPosition(bbox.min_point):
            print("[ERROR][BBox::addBBoxPosition]")
            print("\t addPosition for min_point failed!")
            return False
        if not self.addPosition(bbox.max_point):
            print("[ERROR][BBox::addBBoxPosition]")
            print("\t addPosition for max_point failed!")
            return False
        return True

    def addBBoxListPosition(self, bbox_list):
        for bbox in bbox_list:
            if not self.addBBoxPosition(bbox):
                print("[ERROR][BBox::addBBoxListPosition]")
                print("\t addBBoxPosition failed!")
                return False
        return True

    def updateBBox(self,
                   x_min=None, y_min=None, z_min=None,
                   x_max=None, y_max=None, z_max=None):
        new_x_min = self.min_point.x
        new_y_min = self.min_point.y
        new_z_min = self.min_point.z
        new_x_max = self.max_point.x
        new_y_max = self.max_point.y
        new_z_max = self.max_point.z

        if x_min is not None:
            new_x_min = x_min
        if y_min is not None:
            new_y_min = y_min
        if z_min is not None:
            new_z_min = z_min
        if x_max is not None:
            new_x_max = x_max
        if y_max is not None:
            new_y_max = y_max
        if z_max is not None:
            new_z_max = z_max

        inf = float("inf")
        if new_x_min == inf:
            if new_x_max != -inf:
                new_x_min = new_x_max
        if new_y_min == inf:
            if new_y_max != -inf:
                new_y_min = new_y_max
        if new_z_min == inf:
            if new_z_max != -inf:
                new_z_min = new_z_max

        if new_x_max == -inf:
            if new_x_min != inf:
                new_x_max = new_x_min
        if new_y_max == -inf:
            if new_y_min != inf:
                new_y_max = new_y_min
        if new_z_max == -inf:
            if new_z_min != inf:
                new_z_max = new_z_min

        if new_x_min != inf and new_x_min > new_x_max:
            print("[ERROR][BBox::updateBBox]")
            print("\t input new x size not valid!")
            return False
        if new_y_min != inf and new_y_min > new_y_max:
            print("[ERROR][BBox::updateBBox]")
            print("\t input new y size not valid!")
            return False
        if new_z_min != inf and new_z_min > new_z_max:
            print("[ERROR][BBox::updateBBox]")
            print("\t input new z size not valid!")
            return False

        self.min_point = Point(new_x_min, new_y_min, new_z_min)
        self.max_point = Point(new_x_max, new_y_max, new_z_max)

        self.updateDiffPoint()
        return True

    def getArea(self):
        area = self.diff_point.x * self.diff_point.y
        return area

    def getBoundPointList(self):
        leftdown_point = Point(self.min_point.x, self.min_point.y)
        leftup_point = Point(self.min_point.x, self.max_point.y)
        rightdown_point = Point(self.max_point.x, self.min_point.y)
        rightup_point = Point(self.max_point.x, self.max_point.y)

        bound_point_list = [leftdown_point, leftup_point, rightdown_point, rightup_point]
        return bound_point_list

    def outputInfo(self, info_level):
        line_start = "\t" * info_level
        print(line_start + "[BBox]")
        print(line_start + "\t min_point :")
        self.min_point.outputInfo(info_level + 1)
        print(line_start + "\t max_point :")
        self.max_point.outputInfo(info_level + 1)
        print(line_start + "\t diff_point :")
        self.diff_point.outputInfo(info_level + 1)
        return True

