#!/usr/bin/env python
# -*- coding: utf-8 -*-

import platform

TMP_PATH = ""

if platform.system().lower() == 'windows':
    TMP_PATH = "D:/tmp/"
elif platform.system().lower() == 'linux':
    TMP_PATH = "/home/chli/tmp/"

