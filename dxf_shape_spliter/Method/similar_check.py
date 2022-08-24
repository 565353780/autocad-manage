#!/usr/bin/env python
# -*- coding: utf-8 -*-

from dxf_shape_spliter.Data.line import Line

from dxf_shape_spliter.Method.dists import getPointDist2, getLineDist
from dxf_shape_spliter.Method.cross_check import isBBoxCross, isLineParallel

def getMinConnectLineList(line_1, line_2):
    min_connect_line_list = []
    dist2_ss = getPointDist2(line_1.start_point, line_2.start_point)
    dist2_ee = getPointDist2(line_1.end_point, line_2.end_point)
    dist2_se = getPointDist2(line_1.start_point, line_2.end_point)
    dist2_es = getPointDist2(line_1.end_point, line_2.start_point)

    dist2_1 = dist2_ss + dist2_ee
    dist2_2 = dist2_se + dist2_es

    if dist2_1 < dist2_2:
        min_connect_line_list.append(Line(line_1.start_point, line_2.start_point))
        min_connect_line_list.append(Line(line_1.end_point, line_2.end_point))
        return min_connect_line_list

    min_connect_line_list.append(Line(line_1.start_point, line_2.end_point))
    min_connect_line_list.append(Line(line_1.end_point, line_2.start_point))
    return min_connect_line_list

def isSameLine(line_1, line_2, dist_error_max=0):
    if not isBBoxCross(line_1.bbox, line_2.bbox, dist_error_max):
        return False

    min_connect_line_1, min_connect_line_2 = getMinConnectLineList(line_1, line_2)
    if min_connect_line_1.getLength() > dist_error_max:
        return False
    if min_connect_line_2.getLength() > dist_error_max:
        return False
    return True

def isHaveSameLine(new_line, line_list, dist_error_max=0):
    for line in line_list:
        if isSameLine(new_line, line, dist_error_max):
            return True
    return False

def isLineConnectVertical(line_1, line_2, angle_error_max=0, dist_error_max=0):
    vertical_error_max = 10

    line_1_angle = line_1.getAngle()
    line_2_angle = line_2.getAngle()

    max_angle = max(line_1_angle, line_2_angle)
    min_angle = min(line_1_angle, line_2_angle)

    if min_angle <= 90 + vertical_error_max and max_angle >= 90 - vertical_error_max:
        min_angle += 180

    mean_angle = (line_1_angle + line_2_angle) / 2.0

    connect_line_1, connect_line_2 = getMinConnectLineList(line_1, line_2)
    if connect_line_1.getLength() < dist_error_max and connect_line_2.getLength() < dist_error_max:
        #  print("[WARN][similar_check::isLineConnectVertical]")
        #  print("\t two lines are the same line! seem as not connect vertical by default.")
        return False

    if connect_line_1.getLength() >= dist_error_max:
        connect_line_1_angle = connect_line_1.getAngle()
        angle_diff_1 = abs(mean_angle - connect_line_1_angle - 270)
        angle_diff_2 = abs(mean_angle - connect_line_1_angle - 90)
        angle_diff_3 = abs(mean_angle - connect_line_1_angle + 90)
        angle_diff = min(angle_diff_1, angle_diff_2, angle_diff_3)
        if angle_diff > angle_error_max:
            return False

    if connect_line_2.getLength() >= dist_error_max:
        connect_line_2_angle = connect_line_2.getAngle()
        angle_diff_1 = abs(mean_angle - connect_line_2_angle - 270)
        angle_diff_2 = abs(mean_angle - connect_line_2_angle - 90)
        angle_diff_3 = abs(mean_angle - connect_line_2_angle + 90)
        angle_diff = min(angle_diff_1, angle_diff_2, angle_diff_3)
        if angle_diff > angle_error_max:
            return False
    return True

def isLineSimilar(line_1, line_2, length_error_ratio_max=0, angle_error_max=0, dist_error_max=0):
    if line_1.isPoint() or line_2.isPoint():
        print("[WARN][similar_check::isLineSimilar]")
        print("\t input line contains point! seem as not similar by default.")
        return False

    line_1_length = line_1.getLength()
    line_2_length = line_2.getLength()
    min_length = min(line_1_length, line_2_length)
    if abs(line_1_length - line_2_length) > min_length * length_error_ratio_max:
        return False

    if not isLineParallel(line_1, line_2, angle_error_max):
        return False

    if not isLineConnectVertical(line_1, line_2, angle_error_max, dist_error_max):
        return False

    line_dist = getLineDist(line_1, line_2)
    if line_dist > min_length:
        return False

    return True

def isLineListSimilar(line_list_1, line_list_2,
                      length_error_ratio_max=0, angle_error_max=0, dist_error_max=0):
    for line_1 in line_list_1:
        for line_2 in line_list_2:
            if not isLineSimilar(line_1, line_2,
                                 length_error_ratio_max, angle_error_max, dist_error_max):
                return False
    return True

