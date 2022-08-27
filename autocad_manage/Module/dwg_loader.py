#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import comtypes.client
#  import win32com.client
from tqdm import tqdm

from autocad_manage.Method.path import createFileFolder

class DWGLoader(object):
    def __init__(self):
        self.autocad = None
        self.doc = None

        self.connectAutoCAD()
        return

    def reset(self):
        self.autocad = None
        self.doc = None
        return True

    def connectAutoCAD(self):
        self.reset()

        try:
            self.autocad = comtypes.client.GetActiveObject("AutoCAD.Application")
        except:
            print("[ERROR][DWGLoader::connectAutoCAD]")
            print("\t GetActiveObject failed! please start AutoCAD first!")
            return False

        self.autocad.Visible = True
        return True

    def sendCMD(self, cmd):
        doc = None
        try:
            doc = self.autocad.activedocument
        except:
            print("[ERROR][DWGLoader::sendCMD]")
            print("\t select activedocument failed!")
            return False

        try:
            doc.SendCommand(cmd)
        except:
            print("[ERROR][DWGLoader::sendCMD]")
            print("\t SendCommand failed!")
            print("\t", cmd)
            return False
        return True

    def openDWGFile(self, dwg_file_path):
        if not os.path.exists(dwg_file_path):
            print("[ERROR][DWGLoader::openDWGFile]")
            print("\t dwg_file not exist!")
            return False

        if self.autocad is None:
            print("[ERROR][DWGLoader::openDWGFile]")
            print("\t autocad not connected!")
            return False

        try:
            self.doc = self.autocad.Documents.Open(dwg_file_path)
        except:
            print("[ERROR][DWGLoader::openDWGFile]")
            print("\t Open failed! please check if file exist!")
            print("\t", dwg_file_path)
            return False

        cmd = "FILEDIA " + "0 "
        if not self.sendCMD(cmd):
            print("[ERROR][DWGLoader::openDWGFile]")
            print("\t set FILEDIA to 0 failed!")
            return False
        return True

    def saveAs(self, save_file_path):
        createFileFolder(save_file_path)

        cmd = "SAVEAS " + "dxf " + "16 " + save_file_path + "\n"
        if not self.sendCMD(cmd):
            print("[ERROR][DWGLoader::saveAs]")
            print("\t sendCMD failed!")
            return False
        return True

    def closeDoc(self):
        cmd = "CLOSE "
        if not self.sendCMD(cmd):
            print("[ERROR][DWGLoader::closeDoc]")
            print("\t sendCMD failed!")
            return False
        return True

def demo():
    dwg_file_path = \
        "L:/CAD/House_1/20210223/C00000103/1e9a1ce8f2104613bfa4882cff473c42.dwg"
    save_file_path = \
        "L:/CAD/DXF/House_1/20210223/C00000103/1e9a1ce8f2104613bfa4882cff473c42.dxf"

    dwg_file_path = \
        "L:/CAD/户型识别文件/1.dwg"
    save_file_path = \
        "L:/1.dxf"

    dwg_loader = DWGLoader()
    dwg_loader.openDWGFile(dwg_file_path)
    dwg_loader.saveAs(save_file_path)
    return True

def demo_folder():
    dwg_folder_path = "L:/CAD/户型识别文件/"
    save_folder_path = "L:/CAD/DXF/户型识别文件/"

    dwg_loader = DWGLoader()

    file_path_pair_list = []
    for root, _, files in os.walk(dwg_folder_path):
        for file_name in files:
            if file_name[-4:] != ".dwg":
                continue
            dwg_file_path = root + file_name
            save_file_path = \
                root.replace(dwg_folder_path, save_folder_path) + \
                file_name[:-4] + ".dxf"
            file_path_pair_list.append([dwg_file_path, save_file_path])

    print("[INFO][DWGLoader::demo_folder]")
    print("\t start save dxf files...")
    for file_path_pair in tqdm(file_path_pair_list):
        dwg_file_path, save_file_path = file_path_pair

        if os.path.exists(save_file_path):
            continue

        tmp_file_path = save_file_path[:-4] + "_tmp.dxf"

        dwg_loader.openDWGFile(dwg_file_path)
        dwg_loader.saveAs(tmp_file_path)
        dwg_loader.closeDoc()

        if not os.path.exists(tmp_file_path):
            print("[ERROR][DWGLoader::demo_folder]")
            print("\t save dxf file failed!")
            return False

        while os.path.exists(tmp_file_path):
            try:
                os.rename(tmp_file_path, save_file_path)
            except:
                continue
    return True

