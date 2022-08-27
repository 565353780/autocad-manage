#!/usr/bin/env python
# -*- coding: utf-8 -*-

import numpy as np

from autocad_manage.Data.point import Point

from autocad_manage.Method.dists import getLineDist
from autocad_manage.Method.cross_check import isPointCrossLineList
from autocad_manage.Method.similar_check import getMinConnectLineList

def getMaxDistLineIdxPair(line_list):
    max_dist_line_idx_pair = [-1, -1]
    max_dist = -float('inf')
    for i in range(len(line_list) - 1):
        for j in range(i + 1, len(line_list)):
            current_dist = getLineDist(line_list[i], line_list[j])
            if current_dist > max_dist:
                max_dist_line_idx_pair = [i, j]
                max_dist = current_dist
    return max_dist_line_idx_pair

def getConnectLinePair(line_list):
    max_dist_line_idx_pair = getMaxDistLineIdxPair(line_list)
    connect_line_pair = getMinConnectLineList(
        line_list[max_dist_line_idx_pair[0]], line_list[max_dist_line_idx_pair[1]])
    return connect_line_pair

def getSortedLineIdxList(line_list):
    if len(line_list) < 3:
        return [i for i in range(len(line_list))]

    is_line_selected_list = [False for _ in line_list]

    fix_line_idx, max_dist_line_idx = getMaxDistLineIdxPair(line_list)

    fix_line = line_list[fix_line_idx]
    is_line_selected_list[fix_line_idx] = True

    sorted_line_idx_list = [max_dist_line_idx]
    is_line_selected_list[max_dist_line_idx] = True

    for _ in range(len(line_list) - 2):
        unselected_line_list = [fix_line]
        unselected_line_idx_map_dict = {}
        idx_append_idx = 1
        for i in range(len(line_list)):
            if is_line_selected_list[i]:
                continue
            unselected_line_list.append(line_list[i])
            unselected_line_idx_map_dict[str(idx_append_idx)] = i
            idx_append_idx += 1

        _, max_dist_line_idx = getMaxDistLineIdxPair(unselected_line_list)
        line_list_idx = unselected_line_idx_map_dict[str(max_dist_line_idx)]
        sorted_line_idx_list.append(line_list_idx)
        is_line_selected_list[line_list_idx] = True

    sorted_line_idx_list.append(fix_line_idx)
    return sorted_line_idx_list

def isLineConnectInLineList(line, line_list, dist_error_max=0):
    sample_num = 4

    start_x = line.start_point.x
    start_y = line.start_point.y
    start_z = line.start_point.z
    end_x = line.end_point.x
    end_y = line.end_point.y
    end_z = line.end_point.z

    for i in range(1, sample_num + 1):
        current_step = 1.0 * i / (sample_num + 1)
        current_point = Point(start_x + current_step * (end_x - start_x),
                              start_y + current_step * (end_y - start_y),
                              start_z + current_step * (end_z - start_z))
        if not isPointCrossLineList(current_point, line_list, dist_error_max):
            return False
    return True

def isLineListConnectInAllLineList(line_list, all_line_list, dist_error_max=0):
    sorted_line_idx_list = getSortedLineIdxList(line_list)

    for i in range(len(line_list) - 1):
        connect_line_1, connect_line_2 = getMinConnectLineList(
            line_list[sorted_line_idx_list[i]],
            line_list[sorted_line_idx_list[i + 1]])
        if not isLineConnectInLineList(connect_line_1, all_line_list, dist_error_max):
            return False

        if not isLineConnectInLineList(connect_line_2, all_line_list, dist_error_max):
            return False

    return True

def isLineListUniform(line_list, var_min=2000):
    if len(line_list) < 3:
        return True

    sorted_line_idx_list = getSortedLineIdxList(line_list)

    line_dist_list = []
    for i in range(len(line_list) - 1):
        current_line_dist = getLineDist(line_list[sorted_line_idx_list[i]],
                                        line_list[sorted_line_idx_list[i + 1]])
        line_dist_list.append(current_line_dist)

    var = np.var(line_dist_list)

    if var > var_min:
        return False
    return True

