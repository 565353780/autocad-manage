#!/usr/bin/env python
# -*- coding: utf-8 -*-

from autocad_manage.Module.dxf_loader import DXFLoader


def demo():
    dxf_file_path = "/home/chli/chLi/CAD/DXF/订单图纸/40mm层板生产详图+台面图用于时光木语2.dxf"
    save_json_file_path = "/home/chli/chLi/CAD/JSON/订单图纸/40mm层板生产详图+台面图用于时光木语2.json"

    dxf_loader = DXFLoader(dxf_file_path)
    dxf_loader.outputInfo()
    dxf_loader.saveJson(save_json_file_path)
    return True


def demo_folder():
    dxf_folder_path = "L:/CAD/DXF/户型识别文件/"
    save_folder_path = "L:/CAD/JSON/户型识别文件/"
    print_progress = True

    dxf_loader = DXFLoader()
    dxf_loader.transDxfFolderToJson(dxf_folder_path, save_folder_path,
                                    print_progress)
    return True
