#!/usr/bin/env python
# -*- coding: utf-8 -*-

from math import atan, atan2, pi

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

def isLineParallel(line_1, line_2, angle_error_max=0):
    if line_1.isPoint() or line_2.isPoint():
        print("[WARN][cross_check::isLineParallel]")
        print("\t one of line is a point! set this case as parallel by default")
        return True

    line_1_k = line_1.k
    line_2_k = line_2.k

    if line_1_k == line_2_k:
        return True

    if angle_error_max == 0:
        return False

    line_1_rad = atan(line_1_k)
    line_2_rad = atan(line_2_k)

    rad_diff = abs(line_1_rad - line_2_rad)
    rad_diff_to_pi = abs(rad_diff - pi)

    rad_diff = min(rad_diff, rad_diff_to_pi)

    angle_diff = rad_diff * 180.0 / pi

    if angle_diff < angle_error_max:
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

def isLineCrossWithPool(inputs):
    '''
    Input: [line_1, line_2]
    '''
    if len(inputs) != 2:
        print("[ERROR][cross_check::isLineCrossWithPool]")
        print("\t inputs size != 2!")
        return None
    return isLineCross(inputs[0], inputs[1])

def getLineCrossLineListNum(new_line, line_list):
    line_cross_line_list_num = 0

    for line in line_list:
        if isLineCross(new_line, line):
            line_cross_line_list_num += 1
    return line_cross_line_list_num

def getLineCrossLineListNumWithPool(inputs):
    '''
    Input: [new_line, [line_1, line_2, ...]]
    '''
    if len(inputs) != 2:
        print("[ERROR][cross_check::getLineCrossLineListNumWithPool]")
        print("\t inputs size != 2!")
        return None
    return getLineCrossLineListNum(inputs[0], inputs[1])

def isLineCrossLineList(new_line, line_list):
    line_cross_line_list_num = getLineCrossLineListNum(new_line, line_list)
    if line_cross_line_list_num == 0:
        return False
    return True

def isLineListCross(line_list_1, line_list_2):
    for line in line_list_1:
        if isLineCrossLineList(line, line_list_2):
            return True
    return False

def isLineListCrossWithPool(inputs):
    '''
    Input: [[line_1_1, line_1_2, ...], [line_2_1, line_2_2, ...]]
    '''
    if len(inputs) != 2:
        print("[ERROR][cross_check::isLineListCrossWithPool]")
        print("\t inputs size != 2!")
        return None
    return isLineListCross(inputs[0], inputs[1])

def isPointInArcArea(point, arc):
    point_line = Line(arc.center, point)
    if point_line.isPoint():
        return False

    line_diff_point = point_line.diff_point
    point_line_rad = atan2(line_diff_point.y, line_diff_point.x)
    point_line_angle = point_line_rad * 180.0 / pi

    if arc.start_angle < point_line_angle < arc.end_angle:
        return True
    return False

