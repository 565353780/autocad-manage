#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
from shutil import copyfile

source_folder_path = "/home/chli/chLi/CAD/Image/House_1/"
target_folder_path = "/home/chli/chLi/CAD/20220918_layout_result/"
move_folder_path = "/home/chli/chLi/CAD/20220918_layout_result/"

source_file_path_list = []
for root, _, files in os.walk(source_folder_path):
    for file_name in files:
        if file_name[-4:] != ".png":
            continue
        source_file_path_list.append(root + "/" + file_name)

target_file_name_list = []
for root, _, files in os.walk(target_folder_path):
    for file_name in files:
        if file_name[-4:] != ".png":
            continue
        target_file_name_list.append(file_name)

move_file_path_list = []
for source_file_path in source_file_path_list:
    source_file_name = source_file_path.split("/")[-1]
    if source_file_name not in target_file_name_list:
        move_file_path_list.append(source_file_path)

print(len(source_file_path_list))
print(len(target_file_name_list))
print(len(move_file_path_list))

#  copy_num = 0
#  for source_file_path in move_file_path_list:
    #  source_file_name = source_file_path.split("/")[-1]
    #  copyfile(source_file_path, move_folder_path + source_file_name)
    #  copy_num += 1
    #  if copy_num >= 20:
        #  break

def isSameList(list_1, list_2):
    if len(list_1) != len(list_2):
        return False
    for i in range(len(list_1)):
        if list_1[i] != list_2[i]:
            return False
    return True

total_num = 0

first_label_count_list = []

target_file_label_count_list = []
for root, _, files in os.walk(target_folder_path):
    for file_name in files:
        if file_name[-4:] != ".png":
            continue
        file_label_list = root.split(target_folder_path)[1].split("/")

        total_num += 1

        find_exist_label = False
        for i in range(len(first_label_count_list)):
            if first_label_count_list[i][0] == file_label_list[0]:
                find_exist_label = True
                first_label_count_list[i][1] += 1
                break

        if not find_exist_label:
            first_label_count_list.append([file_label_list[0], 1])

        find_exist_label = False
        for i in range(len(target_file_label_count_list)):
            if isSameList(target_file_label_count_list[i][0], file_label_list):
                find_exist_label = True
                target_file_label_count_list[i][1] += 1
                break

        if not find_exist_label:
            target_file_label_count_list.append([file_label_list, 1])

print()
print("Total dxf layout detect num = " + str(total_num))

print()
for first_label_count in first_label_count_list:
    first_label, count = first_label_count
    percent = int(10000.0 * count / total_num) / 100.0

    print(first_label + " : " + str(count) + " || " + str(percent) + "%")

print()
for target_file_label_count in target_file_label_count_list:
    target_file_label, count = target_file_label_count
    percent = int(10000.0 * count / total_num) / 100.0

    for i in range(len(target_file_label)):
        if i == 0:
            print(target_file_label[i], end="")
            continue
        print(" -> " + target_file_label[i], end="")
    print(" : " + str(count) + " || " + str(percent) + "%")

