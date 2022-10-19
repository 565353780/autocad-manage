#!/usr/bin/env python
# -*- coding: utf-8 -*-

from autocad_manage.Module.autocad_client import AutoCADClient


def demo():
    server_ip = "192.168.2.15"
    server_port = 9366

    dwg_file_path = "/home/chli/chLi/CAD/户型识别文件/1.dwg"
    dwgtodxf_file_path = "/home/chli/chLi/test_dwgtodxf.dxf"
    dxftojson_file_path = "/home/chli/chLi/test_dxftojson.json"
    dwgtojson_file_path = "/home/chli/chLi/test_dwgtojson.json"

    max_client = AutoCADClient(server_ip, server_port)
    max_client.transDwgToDxf(dwg_file_path, dwgtodxf_file_path)
    max_client.transDxfToJson(dwgtodxf_file_path, dxftojson_file_path)
    max_client.transDwgToJson(dwg_file_path, dwgtojson_file_path)

    #  max_client.stop()
    return True
