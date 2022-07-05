#!/usr/bin/env python
# -*- coding: utf-8 -*-

from functools import cmp_to_key
from tqdm import tqdm

from Method.cross_check import isLineListCross
from Method.similar_check import isLineListSimilar

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

def clusterLineByCross(line_list, cluster_label_list, max_dist_error=0):
    last_line_idx_list_list = []
    line_idx_list_list = []
    for i in range(len(line_list)):
        if line_list[i].isMatchAnyLabel(cluster_label_list):
            line_idx_list_list.append([i])

    print("[INFO][cluster::clusterLineByCross]")
    print("\t start merge line clusters...")
    while True:
        if len(line_idx_list_list) < 2:
            break

        last_line_idx_list_list = line_idx_list_list
        line_idx_list_list = []

        for last_line_idx_list in tqdm(last_line_idx_list_list):
            line_list_cross = False
            for i in range(len(line_idx_list_list)):
                last_line_list = [line_list[j] for j in last_line_idx_list]
                current_line_list = [line_list[j] for j in line_idx_list_list[i]]
                if isLineListCross(last_line_list, current_line_list, max_dist_error):
                    line_list_cross = True
                    line_idx_list_list[i] += last_line_idx_list
                    break
            if line_list_cross:
                continue
            line_idx_list_list.append(last_line_idx_list)
        if len(last_line_idx_list_list) == len(line_idx_list_list):
            break
    print("\t merge line clusters finished!")

    line_idx_list_list.sort(key=cmp_to_key(cluster_compare))

    for i, line_idx_list in enumerate(line_idx_list_list):
        for line_idx in line_idx_list:
            line_list[line_idx].setLabel("CrossCluster", i)
    return True

def clusterLineBySimilar(line_list, cluster_label_list,
                         length_error_max=0, angle_error_max=0, dist_error_max=0):
    last_line_idx_list_list = []
    line_idx_list_list = []
    for i in range(len(line_list)):
        if line_list[i].isMatchAnyLabel(cluster_label_list):
            line_idx_list_list.append([i])

    print("[INFO][cluster::clusterLineBySimilar]")
    print("\t start merge line clusters...")
    while True:
        if len(line_idx_list_list) < 2:
            break

        last_line_idx_list_list = line_idx_list_list
        line_idx_list_list = []

        for last_line_idx_list in tqdm(last_line_idx_list_list):
            line_list_cross = False
            for i in range(len(line_idx_list_list)):
                last_line_list = [line_list[j] for j in last_line_idx_list]
                current_line_list = [line_list[j] for j in line_idx_list_list[i]]
                if isLineListSimilar(last_line_list, current_line_list,
                                     length_error_max, angle_error_max, dist_error_max):
                    line_list_cross = True
                    line_idx_list_list[i] += last_line_idx_list
                    break
            if line_list_cross:
                continue
            line_idx_list_list.append(last_line_idx_list)
        if len(last_line_idx_list_list) == len(line_idx_list_list):
            break
    print("\t merge line clusters finished!")

    line_idx_list_list.sort(key=cmp_to_key(cluster_compare))

    for i, line_idx_list in enumerate(line_idx_list_list):
        for line_idx in line_idx_list:
            line_list[line_idx].setLabel("SimilarCluster", i)
    return True

