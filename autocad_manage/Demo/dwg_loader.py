#!/usr/bin/env python
# -*- coding: utf-8 -*-

from autocad_manage.Module.dwg_loader import DWGLoader


def demo():
    dwg_file_path = \
        "L:/CAD/House_1/20210223/C00000103/1e9a1ce8f2104613bfa4882cff473c42.dwg"
    save_file_path = \
        "L:/CAD/output/DXF/House_1/20210223/C00000103/1e9a1ce8f2104613bfa4882cff473c42.dxf"

    dwg_loader = DWGLoader()
    dwg_loader.transDwgToDxf(dwg_file_path, save_file_path)
    return True


def demo_folder():
    dwg_folder_path = "L:/CAD/订单图纸/"
    save_folder_path = "L:/CAD/DXF/订单图纸/"

    dwg_loader = DWGLoader()
    dwg_loader.transDwgFolderToDxf(dwg_folder_path, save_folder_path, True)
    return True

    for i in range(1, 5):
        dwg_folder_path = "L:/CAD/House_" + str(i) + "/"
        save_folder_path = "L:/CAD/DXF/House_" + str(i) + "/"

        dwg_loader = DWGLoader()
        dwg_loader.transDwgFolderToDxf(dwg_folder_path, save_folder_path, True)
    return True
