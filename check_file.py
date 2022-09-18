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
        source_file_path_list.append(root + "/" + file_name)

target_file_name_list = []
for root, _, files in os.walk(target_folder_path):
    for file_name in files:
        target_file_name_list.append(file_name)

move_file_path_list = []
for source_file_path in source_file_path_list:
    source_file_name = source_file_path.split("/")[-1]
    if source_file_name not in target_file_name_list:
        move_file_path_list.append(source_file_path)

print(len(source_file_path_list))
print(len(target_file_name_list))
print(len(move_file_path_list))

for source_file_path in move_file_path_list:
    source_file_name = source_file_path.split("/")[-1]
    copyfile(source_file_path, move_folder_path + source_file_name)

