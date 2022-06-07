#!/usr/bin/env python
# -*- coding: utf-8 -*-

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

