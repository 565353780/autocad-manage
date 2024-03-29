#!/usr/bin/env python
# -*- coding: utf-8 -*-

from autocad_manage.Data.base_shape import BaseShape


class Point(BaseShape):

    def __init__(self, x=0, y=0, z=0):
        super(Point, self).__init__()
        self.x = x
        self.y = y
        self.z = z

        self.type = "POINT"
        return

    def isZero(self):
        if self.x == 0 and self.y == 0 and self.z == 0:
            return True
        return False

    def isFinite(self):
        inf_list = [float("inf"), -float("inf")]
        if self.x in inf_list or self.y in inf_list or self.z in inf_list:
            return False
        return True

    def toList(self):
        return [self.x, self.y, self.z]

    def outputInfo(self, info_level=0):
        line_start = "\t" * info_level
        print(line_start + "[Point]")
        print(line_start + "\t [" + \
              str(self.x) + ", " + \
              str(self.y) + ", " + \
              str(self.z) + "]")
        return True
