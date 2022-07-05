#!/usr/bin/env python
# -*- coding: utf-8 -*-

from Data.line import Line

from Method.dists import getPointDist2, getLineDist
from Method.cross_check import isLineParallel

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

def isLineConnectVertical(line_1, line_2, angle_error_max=0):
    line_1_angle = line_1.getAngle()
    line_2_angle = line_2.getAngle()
    mean_angle = (line_1_angle + line_2_angle) / 2.0
    print("!!!!")
    print(line_1_angle)
    print(line_2_angle)
    print(mean_angle)
    print("!!!!")

    connect_line_1, connect_line_2 = getMinConnectLineList(line_1, line_2)
    if not connect_line_1.isPoint():
        connect_line_1_angle = connect_line_1.getAngle()
        angle_diff = abs(mean_angle - connect_line_1_angle)
        if angle_diff > angle_error_max:
            return False

    if not connect_line_2.isPoint():
        connect_line_2_angle = connect_line_2.getAngle()
        angle_diff = abs(mean_angle - connect_line_2_angle)
        if angle_diff > angle_error_max:
            return False

    return True

def isLineSimilar(line_1, line_2, length_error_max=0, angle_error_max=0):
    if line_1.isPoint() or line_2.isPoint():
        print("[WARN][similar_check::isLineSimilar]")
        print("\t input line contains point! seem as not similar by default.")
        return False

    line_1_length = line_1.getLength()
    line_2_length = line_2.getLength()
    if abs(line_1_length - line_2_length) > length_error_max:
        return False

    if not isLineParallel(line_1, line_2, angle_error_max):
        return False

    if not isLineConnectVertical(line_1, line_2, angle_error_max):
        return False

    mean_length = (line_1_length + line_2_length) / 2.0
    line_dist = getLineDist(line_1, line_2)
    if line_dist > mean_length / 2.0:
        return False

    return True

def isLineListSimilar(line_list_1, line_list_2, length_error_max=0, angle_error_max=0):
    for line_1 in line_list_1:
        for line_2 in line_list_2:
            if not isLineSimilar(line_1, line_2, length_error_max, angle_error_max):
                return False
    return True

