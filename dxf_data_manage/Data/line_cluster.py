#!/usr/bin/env python
# -*- coding: utf-8 -*-

from dxf_data_manage.Data.bbox import BBox

class LineCluster(object):
    def __init__(self, line_list=[]):
        self.line_list = []
        self.bbox = BBox()

        self.addLineList(line_list)
        return

    def reset(self):
        self.line_list = []
        self.bbox = BBox()
        return True

    def addLine(self, line):
        self.line_list.append(line)
        self.bbox.addBBoxPosition(line.bbox)
        return True

    def addLineList(self, line_list):
        if len(line_list) == 0:
            return True

        self.line_list += line_list
        bbox_list = [line.bbox for line in line_list]
        self.bbox.addBBoxListPosition(bbox_list)
        return True

