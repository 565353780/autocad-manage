#!/usr/bin/env python
# -*- coding: utf-8 -*-

from math import sqrt

def getPointDist2(point_1, point_2):
    x_diff = point_1.x - point_2.x
    y_diff = point_1.y - point_2.y
    z_diff = point_1.z - point_2.z
    dist2 = x_diff * x_diff + y_diff * y_diff + z_diff * z_diff
    return dist2

def getPointDist(point_1, point_2):
    dist2 = getPointDist2(point_1, point_2)
    dist = sqrt(dist2)
    return dist

def getLineDist2(line_1, line_2):
    mid_point_1 = line_1.getMiddlePoint()
    mid_point_2 = line_2.getMiddlePoint()
    dist2_mid = getPointDist2(mid_point_1, mid_point_2)

    dist2_ss = getPointDist2(line_1.start_point, line_2.start_point)
    dist2_ee = getPointDist2(line_1.end_point, line_2.end_point)
    dist2_se = getPointDist2(line_1.start_point, line_2.end_point)
    dist2_es = getPointDist2(line_1.end_point, line_2.start_point)

    dist2_1 = dist2_ss + dist2_ee
    dist2_2 = dist2_se + dist2_es

    min_dist2 = min(dist2_1, dist2_2)
    return min_dist2 + dist2_mid

def getLineDist(line_1, line_2):
    mid_point_1 = line_1.getMiddlePoint()
    mid_point_2 = line_2.getMiddlePoint()
    dist_mid = getPointDist(mid_point_1, mid_point_2)

    dist_ss = getPointDist(line_1.start_point, line_2.start_point)
    dist_ee = getPointDist(line_1.end_point, line_2.end_point)
    dist_se = getPointDist(line_1.start_point, line_2.end_point)
    dist_es = getPointDist(line_1.end_point, line_2.start_point)

    dist_1 = dist_ss + dist_ee
    dist_2 = dist_se + dist_es

    min_dist = min(dist_1, dist_2)
    return min_dist + dist_mid

def getMinDistWithLineIdx(line, line_list):
    if len(line_list) == 0:
        print("[ERROR][dists::getMinDistLineIdx]")
        print("\t line_list is empty!")
        return None

    if len(line_list) == 1:
        return 0

    min_dist = float('inf')
    min_dist_idx = -1
    for i in range(len(line_list)):
        current_dist = getLineDist2(line, line_list[i])
        if current_dist < min_dist:
            min_dist = current_dist
            min_dist_idx = i
    return min_dist, min_dist_idx

