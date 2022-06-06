#!/usr/bin/env python
# -*- coding: utf-8 -*-

from functools import cmp_to_key

from Data.shape import Line

def cross(point_1, point_2, point_3):
    x_1 = point_2.x - point_1.x
    y_1 = point_2.y - point_1.y
    x_2 = point_3.x - point_1.x
    y_2 = point_3.y - point_1.y
    cross_value = x_1 * y_2 - x_2 * y_1
    return cross_value

def isBBoxCross(bbox_1, bbox_2):
    if bbox_1.min_point.x > bbox_2.max_point.x or \
            bbox_1.max_point.x < bbox_2.min_point.x or \
            bbox_1.min_point.y > bbox_2.max_point.y or \
            bbox_1.max_point.y < bbox_2.min_point.y:
        return False
    return True

def isLineParallel(line_1, line_2):
    if line_1.isPoint() or line_2.isPoint():
        print("[WARN][cluster::isLineParallel]")
        print("\t one of line is a point! set this case as parallel by default")
        return True

    line_1_x_diff = line_1.bbox.diff_point.x
    line_1_y_diff = line_1.bbox.diff_point.y
    line_2_x_diff = line_2.bbox.diff_point.x
    line_2_y_diff = line_2.bbox.diff_point.y

    if line_1_x_diff == 0:
        if line_2_x_diff != 0:
            return False
        return True

    if line_2_x_diff == 0:
        return True

    line_1_k = line_1_y_diff / line_1_x_diff
    line_2_k = line_2_y_diff / line_2_x_diff

    if line_1_k == line_2_k:
        return True
    return False

def isLineOnSameLine(line_1, line_2):
    if not isLineParallel(line_1, line_2):
        return False

    line_11_to_21 = Line(line_1.start_point, line_2.start_point)

    if line_11_to_21.isPoint():
        return True

    if isLineParallel(line_1, line_11_to_21):
        return True
    return False

def isLineCross(line_1, line_2):
    if not isBBoxCross(line_1.bbox, line_2.bbox):
        return False

    if isLineParallel(line_1, line_2):
        if isLineOnSameLine(line_1, line_2):
            return True
        return False

    cross_1 = cross(line_1.start_point, line_1.end_point, line_2.start_point)
    cross_2 = cross(line_1.start_point, line_1.end_point, line_2.end_point)
    if cross_1 * cross_2 > 0:
        return False

    cross_3 = cross(line_2.start_point, line_2.end_point, line_1.start_point)
    cross_4 = cross(line_2.start_point, line_2.end_point, line_1.end_point)
    if cross_3 * cross_4 > 0:
        return False
    return True

def isLineCrossLineList(new_line, line_list):
    for line in line_list:
        if isLineCross(new_line, line):
            return True
    return False

def isLineListCross(line_list_1, line_list_2):
    for line in line_list_1:
        if isLineCrossLineList(line, line_list_2):
            return True
    return False

def getMergeElementList(list_list, list_idx_list):
    list_list_len = len(list_list)
    list_idx_list = list(set(list_idx_list))

    if len(list_idx_list) < 2:
        print("[WARN][cluster::getMergeElementList]")
        print("\t list_idx_list size < 2!")
        return list_list

    for list_idx in list_idx_list:
        if list_idx >= list_list_len:
            print("[ERROR][cluster::getMergeElementList]")
            print("\t list_idx out of range!")
            return False

    new_list_list = []
    for i in range(len(list_list)):
        if i in list_idx_list:
            continue
        new_list_list.append(list_list[i])

    merge_list = []
    for list_idx in list_idx_list:
        merge_list += list_list[list_idx]
    new_list_list.append(merge_list)
    return new_list_list

def cluster_compare(x, y):
    if len(x) < len(y):
        return 1
    if len(x) > len(y):
        return -1
    return 0

def clusterLine(line_list):
    line_list_list = []

    for line in line_list:
        line_cross = False
        for i in range(len(line_list_list)):
            if isLineCrossLineList(line, line_list_list[i]):
                line_cross = True
                line_list_list[i].append(line)
                break
        if line_cross:
            continue
        line_list_list.append([line])

    print("[INFO][cluster::clusterLine]")
    print("\t start cluster line...")
    while True:
        if len(line_list_list) < 2:
            break

        cross_lines_idx_list = []

        for i in range(len(line_list_list) - 1):
            for j in range(i + 1, len(line_list_list)):
                if isLineListCross(line_list_list[i], line_list_list[j]):
                    cross_lines_idx_list.append(j)
            if len(cross_lines_idx_list) > 0:
                cross_lines_idx_list.append(i)
                break

        if len(cross_lines_idx_list) == 0:
            break
        line_list_list = \
            getMergeElementList(line_list_list, cross_lines_idx_list)
        print("\r\t line_list_list num =",
              len(line_list_list),
              "    ",
              end="")
    print()
    print("\t cluster line finished!")

    line_list_list.sort(key=cmp_to_key(cluster_compare))
    return line_list_list

