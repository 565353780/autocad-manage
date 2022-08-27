#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os

def createFileFolder(file_path):
    file_name = file_path.split("/")[-1]
    file_folder_path = file_path.split(file_name)[0]
    if os.path.exists(file_folder_path):
        return True
    os.makedirs(file_folder_path)
    return True

