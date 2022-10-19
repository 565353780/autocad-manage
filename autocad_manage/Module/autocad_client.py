#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
import requests

from autocad_manage.Method.encode import getBase64Data, saveData


class AutoCADClient(object):

    def __init__(self, server_ip, server_port):
        self.server_ip = server_ip
        self.server_port = server_port

        self.url = "http://" + self.server_ip + ":" + str(
            self.server_port) + "/"
        return

    def getPostResult(self, route, data):
        result = requests.post(self.url + route, data=json.dumps(data)).text
        try:
            result_json = json.loads(result)
        except:
            print("[ERROR][AutoCADClient::getPostResult]")
            print("\t result not valid! result is:")
            print(result)
            return None
        return result_json

    def transDwgToDxf(self, dwg_file_path, save_dxf_file_path):
        dwg_data = getBase64Data(dwg_file_path)
        if dwg_data is None:
            print("[ERROR][AutoCADClient::transDwgToDxf]")
            print("\t getBase64Data failed!")
            return None

        dxf_file_basename = save_dxf_file_path.split("/")[-1].split(".dxf")[0]
        data = {'dwg_data': dwg_data, 'dxf_file_basename': dxf_file_basename}

        result = self.getPostResult('transDwgToDxf', data)
        if result is None:
            print("[ERROR][AutoCADClient::transDwgToDxf]")
            print("\t getPostResult failed!")
            return False

        dxf_data = result['dxf_data']
        if dxf_data is None:
            print("[ERROR][AutoCADClient::transDwgToDxf]")
            print("\t dxf_data is None!")
            return False

        saveData(dxf_data, save_dxf_file_path)
        return True

    def transDxfToJson(self, dxf_file_path, save_json_file_path):
        dxf_data = getBase64Data(dxf_file_path)
        if dxf_data is None:
            print("[ERROR][AutoCADClient::transDxfToJson]")
            print("\t getBase64Data failed!")
            return None

        json_file_basename = save_json_file_path.split("/")[-1].split(
            ".json")[0]
        data = {'dxf_data': dxf_data, 'json_file_basename': json_file_basename}

        result = self.getPostResult('transDxfToJson', data)
        if result is None:
            print("[ERROR][AutoCADClient::transDxfToJson]")
            print("\t getPostResult failed!")
            return False

        json_data = result['json_data']
        if json_data is None:
            print("[ERROR][AutoCADClient::transDxfToJson]")
            print("\t json_data is None!")
            return False

        saveData(json_data, save_json_file_path)
        return True

    def transDwgToJson(self, dwg_file_path, save_json_file_path):
        dwg_data = getBase64Data(dwg_file_path)
        if dwg_data is None:
            print("[ERROR][AutoCADClient::transDwgToJson]")
            print("\t getBase64Data failed!")
            return None

        json_file_basename = save_json_file_path.split("/")[-1].split(
            ".json")[0]
        data = {'dwg_data': dwg_data, 'json_file_basename': json_file_basename}

        result = self.getPostResult('transDwgToJson', data)
        if result is None:
            print("[ERROR][AutoCADClient::transDwgToJson]")
            print("\t getPostResult failed!")
            return False

        json_data = result['json_data']
        if json_data is None:
            print("[ERROR][AutoCADClient::transDwgToJson]")
            print("\t json_data is None!")
            return False

        saveData(json_data, save_json_file_path)
        return True

    def stop(self):
        _ = self.getPostResult('stop', {'stop': 'start'})
        return True
