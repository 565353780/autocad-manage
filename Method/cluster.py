#!/usr/bin/env python
# -*- coding: utf-8 -*-

from functools import cmp_to_key
from tqdm import tqdm

from Method.cross_check import isLineListCross

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
    last_line_list_list = []
    line_list_list = [[line] for line in line_list]

    print("[INFO][cluster::clusterLine]")
    print("\t start merge line clusters...")
    while True:
        if len(line_list_list) < 2:
            break

        last_line_list_list = line_list_list
        line_list_list = []

        for line_list in tqdm(last_line_list_list):
            line_list_cross = False
            for i in range(len(line_list_list)):
                if isLineListCross(line_list, line_list_list[i]):
                    line_list_cross = True
                    line_list_list[i] += line_list
                    break
            if line_list_cross:
                continue
            line_list_list.append(line_list)
        if len(last_line_list_list) == len(line_list_list):
            break
    print("\t merge line clusters finished!")

    line_list_list.sort(key=cmp_to_key(cluster_compare))
    return line_list_list

