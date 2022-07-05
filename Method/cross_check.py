#!/usr/bin/env python
# -*- coding: utf-8 -*-

from math import atan, atan2, pi

from Data.shape import Line

from Method.dists import getPointDist

def cross(point_1, point_2, point_3):
    x_1 = point_2.x - point_1.x
    y_1 = point_2.y - point_1.y
    x_2 = point_3.x - point_1.x
    y_2 = point_3.y - point_1.y
    cross_value = x_1 * y_2 - x_2 * y_1
    return cross_value

def isBBoxCross(bbox_1, bbox_2, max_dist_error=0):
    if bbox_1.min_point.x > bbox_2.max_point.x + max_dist_error or \
            bbox_1.max_point.x < bbox_2.min_point.x - max_dist_error or \
            bbox_1.min_point.y > bbox_2.max_point.y + max_dist_error or \
            bbox_1.max_point.y < bbox_2.min_point.y - max_dist_error:
        return False
    return True

def isPointInBBox(point, bbox, max_dist_error=0):
    if bbox.min_point.x - max_dist_error <= point.x <= bbox.max_point.x + max_dist_error and \
            bbox.min_point.y - max_dist_error <= point.y <= bbox.max_point.y + max_dist_error and \
            bbox.min_point.z - max_dist_error <= point.z <= bbox.max_point.z + max_dist_error:
        return True
    return False

def isPointCrossLine(point, line, max_dist_error=0):
    if not isPointInBBox(point, line.bbox, max_dist_error):
        return False

    point_to_start_point_dist = getPointDist(point , line.start_point)
    if point_to_start_point_dist <= max_dist_error:
        return True

    point_to_end_point_dist = getPointDist(point , line.end_point)
    if point_to_end_point_dist <= max_dist_error:
        return True

    point_line_cross = cross(line.start_point, line.end_point, point)
    point_dist_to_line = abs(point_line_cross) / line.getLength()

    if point_dist_to_line <= max_dist_error:
        return True
    return False

def getPointCrossLineListNum(point, line_list, max_dist_error=0):
    point_cross_line_list_num = 0

    for line in line_list:
        if isPointCrossLine(point, line, max_dist_error):
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

def isLineCross(line_1, line_2, max_dist_error=0):
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
    if min_dist <= max_dist_error:
        return True

    if not isBBoxCross(line_1.bbox, line_2.bbox, max_dist_error):
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

def getLineCrossLineListNum(new_line, line_list, max_dist_error):
    line_cross_line_list_num = 0

    for line in line_list:
        if isLineCross(new_line, line, max_dist_error):
            line_cross_line_list_num += 1
    return line_cross_line_list_num

def isLineCrossLineList(new_line, line_list, max_dist_error=0):
    line_cross_line_list_num = getLineCrossLineListNum(new_line, line_list, max_dist_error)
    if line_cross_line_list_num == 0:
        return False
    return True

def isLineListCross(line_list_1, line_list_2, max_dist_error=0):
    for line in line_list_1:
        if isLineCrossLineList(line, line_list_2, max_dist_error):
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

