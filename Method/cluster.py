#!/usr/bin/env python
# -*- coding: utf-8 -*-

from functools import cmp_to_key
from tqdm import tqdm

from Data.line_cluster import LineCluster

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

def clusterLine(line_list, max_dist_error=0):
    last_line_list_list = []
    line_list_list = [[line] for line in line_list]

    print("[INFO][cluster::clusterLine]")
    print("\t start merge line clusters...")
    while True:
        if len(line_list_list) < 2:
            break

        last_line_list_list = line_list_list
        line_list_list = []

        for last_line_list in tqdm(last_line_list_list):
            line_list_cross = False
            for i in range(len(line_list_list)):
                if isLineListCross(last_line_list, line_list_list[i], max_dist_error):
                    line_list_cross = True
                    line_list_list[i] += last_line_list
                    break
            if line_list_cross:
                continue
            line_list_list.append(last_line_list)
        if len(last_line_list_list) == len(line_list_list):
            break
    print("\t merge line clusters finished!")

    line_list_list.sort(key=cmp_to_key(cluster_compare))
    return line_list_list

def isLineHaveLabel(line, label_list):
    for label in label_list:
        label_value = line.getLabel(label)
        if label_value is not None:
            return True
    return False

def changeClusterIdx(line_list, old_idx, new_idx):
    for line in line_list:
        cluster_label = line.getLabel("Cluster")
        if cluster_label is None:
            continue
        if cluster_label != old_idx:
            continue
        line.setLabel("Cluster", new_idx)
    return True

def getClusterNum(line_list):
    cluster_num_dict = {}
    for line in line_list:
        cluster_idx = line.getLabel("Cluster")
        if cluster_idx is None:
            continue
        if str(cluster_idx) not in cluster_num_dict.keys():
            cluster_num_dict[str(cluster_idx)] = 1
        else:
            cluster_num_dict[str(cluster_idx)] += 1
    print(cluster_num_dict)
    return True

def clusterLineByIdx(line_list, cluster_label_list, max_dist_error=0):
    last_line_idx_list_list = []
    line_idx_list_list = []
    for i in range(len(line_list)):
        if isLineHaveLabel(line_list[i], cluster_label_list):
            line_idx_list_list.append([i])

    print("[INFO][cluster::clusterLineByIdx]")
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

    line_cluster_list = []

    for i, line_idx_list in enumerate(line_idx_list_list):
        line_cluster = LineCluster()
        for line_idx in line_idx_list:
            line_list[line_idx].setLabel("Cluster", i)
            line_cluster.addLine(line_list[line_idx])
        line_cluster_list.append(line_cluster)
    return line_cluster_list

