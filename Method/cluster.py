#!/usr/bin/env python
# -*- coding: utf-8 -*-

from functools import cmp_to_key

from Method.cross_check import \
    isLineCrossLineList, isLineListCross

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
        print("\r\t line_list_list num =", len(line_list_list), "    ", end="")
    print()
    print("\t cluster line finished!")

    line_list_list.sort(key=cmp_to_key(cluster_compare))
    return line_list_list

