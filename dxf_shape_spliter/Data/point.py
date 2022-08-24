#!/usr/bin/env python
# -*- coding: utf-8 -*-

from dxf_shape_spliter.Data.label import Label

class Point(Label):
    def __init__(self, x=0, y=0, z=0):
        super(Point, self).__init__()
        self.x = x
        self.y = y
        self.z = z
        return

    def isZero(self):
        if self.x == 0 and self.y == 0 and self.z == 0:
            return True
        return False

    def outputInfo(self, info_level):
        line_start = "\t" * info_level
        print(line_start + "[Point]")
        print(line_start + "\t [" + \
              str(self.x) + ", " + \
              str(self.y) + ", " + \
              str(self.z) + "]")
        return True

