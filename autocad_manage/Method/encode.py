#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
from base64 import b64encode, b64decode

from autocad_manage.Method.path import createFileFolder

def getBase64Data(file_path):
    if not os.path.exists(file_path):
        print("[ERROR][encode::getBase64Data]")
        print("\t file not exist!")
        return None

    with open(file_path, 'rb') as f:
        file_data = f.read()
        base64_data = b64encode(file_data).decode().encode('utf-8').decode('utf-8')
        return base64_data

def getDecodeData(base64_data):
    decode_data = b64decode(base64_data)
    return decode_data

def saveData(base64_data, file_path):
    createFileFolder(file_path)

    decode_data = getDecodeData(base64_data)
    with open(file_path, "wb") as f:
        f.write(decode_data)
    return True

