#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
sys.path.append("../method-manage/")

import os

from method_manage.Config.path import TMP_SAVE_FOLDER_PATH

from method_manage.Method.path import removeIfExist
from method_manage.Method.signal import getDataIn, sendDataOut
from method_manage.Method.encode import getBase64Data, saveData

from autocad_manage.Module.dwg_loader import DWGLoader
from autocad_manage.Module.dxf_loader import DXFLoader

class AutoCADServer(object):
    def __init__(self):
        self.dwg_loader = DWGLoader()
        self.dxf_loader = DXFLoader()
        return

    def receiveFile(self):
        data = getDataIn('receiveFile')
        if data is None:
            return True

        file_data = data['file_data']
        file_name = data['file_name']
        file_path = TMP_SAVE_FOLDER_PATH + file_name
        saveData(file_data, file_path)

        result = {'state': 'success'}
        sendDataOut('receiveFile', result)
        return True

    def sendFile(self):
        data = getDataIn('sendFile')
        if data is None:
            return True

        result = {
            'file_data': None,
        }

        file_name = data['file_name']
        file_path = TMP_SAVE_FOLDER_PATH + file_name
        if not os.path.exists(file_path):
            print("[WARN][AutoCADServer::sendFile]")
            print("\t file not exist!")
            sendDataOut('receiveFile', result)
            return False

        result['file_data'] = getBase64Data(file_path)
        sendDataOut('sendFile', result)

    def loadDWGFile(self):
        data = getDataIn('loadDWGFile')
        if data is None:
            return True

        file_name = data['file_name']
        file_path = TMP_SAVE_FOLDER_PATH + file_name
        if not os.path.exists(file_path):
            print("[ERROR][AutoCADServer::loadDWGFile]")
            print("\t file not exist!")

            result = {'state': 'failed'}
            sendDataOut('loadDWGFile', result)
            return False

        if not self.dwg_loader.openDWGFile(file_path):
            print("[ERROR][AutoCADServer::loadDWGFile]")
            print("\t openDWGFile failed!")

            result = {'state': 'failed'}
            sendDataOut('loadDWGFile', result)
            return False

        result = {'state': 'success'}
        sendDataOut('loadDWGFile', result)
        return True

    def saveAsDxf(self):
        data = getDataIn('saveAsDxf')
        if data is None:
            return True

        file_name = data['file_name']

        file_save_path = TMP_SAVE_FOLDER_PATH + file_name
        if not self.dwg_loader.saveAs(file_save_path):
            print("[ERROR][AutoCADServer::saveAsDxf]")
            print("\t exportAll failed!")

            result = {'state': 'failed'}
            sendDataOut('saveAsDxf', result)
            return False

        result = {'state': 'success'}
        sendDataOut('saveAsDxf', result)
        return True

    def transDwgToDxf(self):
        data = getDataIn('transDwgToDxf')
        if data is None:
            return True

        dwg_data = data['dwg_data']
        dxf_file_basename = data['dxf_file_basename']

        dwg_file_path = TMP_SAVE_FOLDER_PATH + dxf_file_basename + ".dwg"
        saveData(dwg_data, dwg_file_path)

        save_dxf_file_path = TMP_SAVE_FOLDER_PATH + dxf_file_basename + ".dxf"
        if not self.dwg_loader.transDwgToDxf(dwg_file_path, save_dxf_file_path):
            print("[ERROR][AutoCADServer::transDwgToDxf]")
            print("\t transDwgToDxf failed!")
            return False

        removeIfExist(dwg_file_path)

        dxf_data = getBase64Data(save_dxf_file_path)
        result = {
            'dxf_data': dxf_data,
        }

        removeIfExist(save_dxf_file_path)

        sendDataOut('transDwgToDxf', result)
        return True

    def transDxfToJson(self):
        data = getDataIn('transDxfToJson')
        if data is None:
            return True

        dxf_data = data['dxf_data']
        json_file_basename = data['json_file_basename']

        dxf_file_path = TMP_SAVE_FOLDER_PATH + json_file_basename + ".dxf"
        saveData(dxf_data, dxf_file_path)

        save_json_file_path = TMP_SAVE_FOLDER_PATH + json_file_basename + ".json"
        if not self.dxf_loader.transDxfToJson(dxf_file_path, save_json_file_path):
            print("[ERROR][AutoCADServer::transDxfToJson]")
            print("\t transDxfToJson failed!")
            return False

        removeIfExist(dxf_file_path)

        json_data = getBase64Data(save_json_file_path)
        result = {
            'json_data': json_data,
        }

        removeIfExist(save_json_file_path)

        sendDataOut('transDxfToJson', result)
        return True

    def transDwgToJson(self):
        data = getDataIn('transDwgToJson')
        if data is None:
            return True

        dwg_data = data['dwg_data']
        json_file_basename = data['json_file_basename']

        dwg_file_path = TMP_SAVE_FOLDER_PATH + json_file_basename + ".dwg"
        saveData(dwg_data, dwg_file_path)

        save_dxf_file_path = TMP_SAVE_FOLDER_PATH + json_file_basename + ".dxf"
        save_json_file_path = TMP_SAVE_FOLDER_PATH + json_file_basename + ".json"
        if not self.dwg_loader.transDwgToDxf(dwg_file_path, save_dxf_file_path):
            print("[ERROR][AutoCADServer::transDwgToJson]")
            print("\t transDwgToDxf failed!")
            return False

        removeIfExist(dwg_file_path)

        if not self.dxf_loader.transDxfToJson(save_dxf_file_path, save_json_file_path):
            print("[ERROR][AutoCADServer::transDwgToJson]")
            print("\t transDxfToJson failed!")
            return False

        removeIfExist(save_dxf_file_path)

        json_data = getBase64Data(save_json_file_path)
        result = {
            'json_data': json_data,
        }

        removeIfExist(save_json_file_path)

        sendDataOut('transDwgToJson', result)
        return True

    def clear(self):
        data = getDataIn('clear')
        if data is None:
            return False

        for file_name in os.listdir(TMP_SAVE_FOLDER_PATH):
            file_path = TMP_SAVE_FOLDER_PATH + file_name
            removeIfExist(file_path)

        result = {'state': 'stop success'}
        sendDataOut('clear', result)
        return True

    def stop(self):
        data = getDataIn('stop')
        if data is None:
            return False

        result = {'state': 'stop success'}
        sendDataOut('stop', result)
        return True
    
    def start(self):
        while True:
            self.receiveFile()
            self.sendFile()
            self.loadDWGFile()
            self.saveAsDxf()
            self.transDwgToDxf()
            self.transDxfToJson()
            self.transDwgToJson()
            self.clear()

            if self.stop():
                break
        return True

def demo():
    autocad_server = AutoCADServer()
    autocad_server.start()
    return True

