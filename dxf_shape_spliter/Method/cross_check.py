#!/usr/bin/env python
# -*- coding: utf-8 -*-

from math import atan2, pi

from dxf_shape_spliter.Data.shape import Line

from dxf_shape_spliter.Method.dists import getPointDist

def cross(point_1, point_2, point_3):
    x_1 = point_2.x - point_1.x
    y_1 = point_2.y - point_1.y
    x_2 = point_3.x - point_1.x
    y_2 = point_3.y - point_1.y
    cross_value = x_1 * y_2 - x_2 * y_1
    return cross_value

def isBBoxCross(bbox_1, bbox_2, dist_error_max=0):
    if bbox_1.min_point.x > bbox_2.max_point.x + dist_error_max or \
            bbox_1.max_point.x < bbox_2.min_point.x - dist_error_max or \
            bbox_1.min_point.y > bbox_2.max_point.y + dist_error_max or \
            bbox_1.max_point.y < bbox_2.min_point.y - dist_error_max:
        return False
    return True

def isPointInBBox(point, bbox, dist_error_max=0):
    if bbox.min_point.x - dist_error_max <= point.x <= bbox.max_point.x + dist_error_max and \
            bbox.min_point.y - dist_error_max <= point.y <= bbox.max_point.y + dist_error_max and \
            bbox.min_point.z - dist_error_max <= point.z <= bbox.max_point.z + dist_error_max:
        return True
    return False

def isPointCrossLine(point, line, dist_error_max=0):
    if not isPointInBBox(point, line.bbox, dist_error_max):
        return False

    point_to_start_point_dist = getPointDist(point , line.start_point)
    if point_to_start_point_dist <= dist_error_max:
        return True

    point_to_end_point_dist = getPointDist(point , line.end_point)
    if point_to_end_point_dist <= dist_error_max:
        return True

    point_line_cross = cross(line.start_point, line.end_point, point)
    point_dist_to_line = abs(point_line_cross) / line.getLength()

    if point_dist_to_line <= dist_error_max:
        return True
    return False

def isPointCrossLineList(point, line_list, dist_error_max=0):
    for line in line_list:
        if isPointCrossLine(point, line, dist_error_max):
            return True
    return False

def getPointCrossLineListNum(point, line_list, dist_error_max=0):
    point_cross_line_list_num = 0

    for line in line_list:
        if isPointCrossLine(point, line, dist_error_max):
            point_cross_line_list_num += 1
    return point_cross_line_list_num

def isLineHorizontal(line, k_0_max=0):
    line_k = line.k
    if line_k == 0:
        return True

    if k_0_max == 0:
        return False

    abs_line_k = abs(line_k)
    if abs_line_k < k_0_max:
        return True

    return False

def isLineVertical(line, k_inf_min=float('inf')):
    line_k = line.k
    if line_k == float('inf'):
        return True

    if k_inf_min == float('inf'):
        return False

    abs_line_k = abs(line_k)
    if abs_line_k > k_inf_min:
        return True

    return False

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

    line_1_angle = line_1.getAngle()
    line_2_angle = line_2.getAngle()

    angle_diff_1 = abs(line_1_angle - line_2_angle)
    angle_diff_2 = abs(line_1_angle - line_2_angle - 180)

    angle_diff = min(angle_diff_1, angle_diff_2)

    if angle_diff < angle_error_max:
        return True
    return False

def isLineOnSameLine(line_1, line_2, angle_error_max=0, dist_error_max=0):
    if not isLineParallel(line_1, line_2, angle_error_max):
        return False

    line_11_to_21 = Line(line_1.start_point, line_2.start_point)

    if line_11_to_21.getLength() <= dist_error_max:
        return True

    if isLineParallel(line_1, line_11_to_21, angle_error_max):
        return True
    return False

def isLineListOnSameLines(line_list_1, line_list_2, angle_error_max=0, dist_error_max=0):
    for line_1 in line_list_1:
        for line_2 in line_list_2:
            if not isLineParallel(line_1, line_2, angle_error_max):
                return False

    is_line_list_2_contain_line_list_1 = True
    for line_1 in line_list_1:
        find_same_line = False
        for line_2 in line_list_2:
            if isLineOnSameLine(line_1, line_2, angle_error_max, dist_error_max):
                find_same_line = True
                break

        if not find_same_line:
            is_line_list_2_contain_line_list_1 = False
            break

    if is_line_list_2_contain_line_list_1:
        return True

    is_line_list_1_contain_line_list_2 = True
    for line_2 in line_list_2:
        find_same_line = False
        for line_1 in line_list_1:
            if isLineOnSameLine(line_2, line_1, angle_error_max, dist_error_max):
                find_same_line = True
                break

        if not find_same_line:
            is_line_list_1_contain_line_list_2 = False
            break

    if is_line_list_1_contain_line_list_2:
        return True
    return False

def isLineCross(line_1, line_2, dist_error_max=0, angle_error_max=0):
    dist_ss = getPointDist(line_1.start_point, line_2.start_point)
    if dist_ss == 0:
        return True

    dist_se = getPointDist(line_1.start_point, line_2.end_point)
    if dist_se == 0:
        return True

    dist_es = getPointDist(line_1.end_point, line_2.start_point)
    if dist_es == 0:
        return True

    dist_ee = getPointDist(line_1.end_point, line_2.end_point)
    if dist_ee == 0:
        return True

    min_dist = min(dist_ss, dist_se, dist_es, dist_ee)
    if min_dist <= dist_error_max:
        return True

    if not isBBoxCross(line_1.bbox, line_2.bbox, dist_error_max):
        return False

    if isLineParallel(line_1, line_2, angle_error_max):
        if isLineOnSameLine(line_1, line_2, angle_error_max, dist_error_max):
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

def getLineCrossLineListNum(new_line, line_list, dist_error_max):
    line_cross_line_list_num = 0

    for line in line_list:
        if isLineCross(new_line, line, dist_error_max):
            line_cross_line_list_num += 1
    return line_cross_line_list_num

def isLineCrossLineList(new_line, line_list, dist_error_max=0):
    line_cross_line_list_num = getLineCrossLineListNum(new_line, line_list, dist_error_max)
    if line_cross_line_list_num == 0:
        return False
    return True

def isLineListCross(line_list_1, line_list_2, dist_error_max=0):
    for line in line_list_1:
        if isLineCrossLineList(line, line_list_2, dist_error_max):
            return True
    return False

def isPointCrossArc(point, arc, dist_error_max=0):
    line_list = []
    for i in range(len(arc.flatten_point_list) - 1):
        arc_line = Line(arc.flatten_point_list[i], arc.flatten_point_list[i + 1])
        line_list.append(arc_line)
    return isPointCrossLineList(point, line_list, dist_error_max)

def isLineCrossArc(line, arc, dist_error_max=0):
    line_list = []
    for i in range(len(arc.flatten_point_list) - 1):
        arc_line = Line(arc.flatten_point_list[i], arc.flatten_point_list[i + 1])
        line_list.append(arc_line)
    return isLineCrossLineList(line, line_list, dist_error_max)

def isLineCrossArcList(line, arc_list, dist_error_max=0):
    for arc in arc_list:
        if isLineCrossArc(line, arc, dist_error_max):
            return True
    return False

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

