#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import json

from autocad_manage.Config.path import TMP_SAVE_FOLDER_PATH

from autocad_manage.Method.path import createFileFolder, removeIfExist

def getSignal(signal, status="", file_format="txt"):
    signal_file_name = signal
    if status != "":
        signal_file_name += "_" + status
    signal_file_name += "." + file_format
    return signal_file_name

def getStartSignal(signal):
    return getSignal(signal)

def getDataInJson(signal):
    return getSignal(signal, file_format="json")

def getDataOutJson(signal):
    return getSignal(signal, "finish", "json")

def getFinishSignal(signal):
    return getSignal(signal, "finish")

def writeData(data_file_path, data, format="wb"):
    createFileFolder(data_file_path)

    with open(data_file_path, format) as f:
        f.write(data)
    return True

def sendSignal(signal_file_name, data="1"):
    signal_file_path = TMP_SAVE_FOLDER_PATH + signal_file_name
    createFileFolder(signal_file_path)

    with open(signal_file_path, "w") as f:
        f.write(data)
    return True

def sendDataIn(signal, data):
    data_in_json = getDataInJson(signal)
    data_file_path = TMP_SAVE_FOLDER_PATH + data_in_json
    writeData(data_file_path, data)

    start_signal = getStartSignal(signal)
    sendSignal(start_signal)
    return True

def getDataIn(signal):
    start_signal = getStartSignal(signal)
    signal_file_path = TMP_SAVE_FOLDER_PATH + start_signal
    if not os.path.exists(signal_file_path):
        return None

    removeIfExist(signal_file_path)

    data_in_json = getDataInJson(signal)
    data_file_path = TMP_SAVE_FOLDER_PATH + data_in_json
    if not os.path.exists(data_file_path):
        print("[ERROR][signal::getDataIn]")
        print("\t data_file not exist!")
        return None

    with open(data_file_path, "rb") as f:
        data = f.read()
    data_json = json.loads(data)

    removeIfExist(data_file_path)
    return data_json

def sendDataOut(signal, data_json):
    data_out_json = getDataOutJson(signal)
    data_file_path = TMP_SAVE_FOLDER_PATH + data_out_json

    data = json.dumps(data_json)
    writeData(data_file_path, data, "w")

    finish_signal = getFinishSignal(signal)
    sendSignal(finish_signal)
    return True

def getDataOut(signal):
    finish_signal = getFinishSignal(signal)
    signal_file_path = TMP_SAVE_FOLDER_PATH + finish_signal
    while not os.path.exists(signal_file_path):
        continue

    removeIfExist(signal_file_path)

    data = None
    data_out_json = getDataOutJson(signal)
    data_file_path = TMP_SAVE_FOLDER_PATH + data_out_json
    with open(data_file_path, "r") as f:
        data = f.read()
    data_json = json.loads(data)

    removeIfExist(data_file_path)
    return data_json

