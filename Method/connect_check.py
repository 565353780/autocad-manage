#!/usr/bin/env python
# -*- coding: utf-8 -*-

from Data.point import Point

from Method.dists import getLineDist
from Method.cross_check import isPointCrossLineList
from Method.similar_check import getMinConnectLineList

def getConnectLinePair(line_list):
    max_dist_line_idx_pair = [-1, -1]
    max_dist = -float('inf')
    for i in range(len(line_list) - 1):
        for j in range(i + 1, len(line_list)):
            current_dist = getLineDist(line_list[i], line_list[j])
            if current_dist > max_dist:
                max_dist_line_idx_pair = [i, j]
                max_dist = current_dist

    connect_line_pair = getMinConnectLineList(
        line_list[max_dist_line_idx_pair[0]], line_list[max_dist_line_idx_pair[1]])
    return connect_line_pair

def isLineConnectInLineList(line, line_list, dist_error_max=0):
    sample_num = 10

    start_x = line.start_point.x
    start_y = line.start_point.y
    start_z = line.start_point.z
    end_x = line.end_point.x
    end_y = line.end_point.y
    end_z = line.end_point.z

    for i in range(1, sample_num):
        current_step = 1.0 * i / sample_num
        current_point = Point(start_x + current_step * (end_x - start_x),
                              start_y + current_step * (end_y - start_y),
                              start_z + current_step * (end_z - start_z))
        if not isPointCrossLineList(current_point, line_list, dist_error_max):
            return False
    return True

def isLineListConnectInAllLineList(line_list, all_line_list, dist_error_max=0):

    connect_line_1, connect_line_2 = getConnectLinePair(line_list)

    if not isLineConnectInLineList(connect_line_1, all_line_list, dist_error_max):
        return False

    if not isLineConnectInLineList(connect_line_2, all_line_list, dist_error_max):
        return False
    return True

