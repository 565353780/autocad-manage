#!/usr/bin/env python
# -*- coding: utf-8 -*-

import platform

TMP_SAVE_FOLDER_PATH = ""
if platform.system().lower() == 'windows':
    TMP_SAVE_FOLDER_PATH = "P:/tmp/"
elif platform.system().lower() == 'linux':
    TMP_SAVE_FOLDER_PATH = "/home/chli/public/tmp/"

