#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import comtypes.client
#  import win32com.client

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

    def resetAutoCAD(self):
        if self.autocad is None:
            return True
        self.sendCMD("FILEDIA 1")
        return True

    def connectAutoCAD(self):
        self.reset()

        try:
            self.autocad = comtypes.client.GetActiveObject("AutoCAD.Application")
        except:
            print("[ERROR][DWGLoader::connectAutoCAD]")
            print("\t GetActiveObject failed! please start AutoCAD first!")
            return False

        self.sendCMD("FILEDIA 0")
        self.autocad.Visible = True
        return True

    def sendCMD(self, cmd):
        doc = self.autocad.activedocument
        doc.SendCommand(cmd)
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
        return True

    def saveAs(self, save_file_path):
        createFileFolder(save_file_path)
        self.autocad.Documents.SaveAs(save_file_path)
        return True

def demo():
    dwg_file_path = \
        "L:/CAD/House_1/20210223/C00000103/1e9a1ce8f2104613bfa4882cff473c42.dwg"
    save_file_path = \
        "L:/CAD/DXF/House_1/20210223/C00000103/1e9a1ce8f2104613bfa4882cff473c42.dwg"
    dwg_loader = DWGLoader()
    dwg_loader.openDWGFile(dwg_file_path)
    dwg_loader.sendCMD("SAVEAS " + save_file_path)
    dwg_loader.saveAs(save_file_path)
    return True

def demo_folder():
    dwg_folder_path = "L:/CAD/"
    save_folder_path = "L:/CAD/DXF/"

    dwg_loader = DWGLoader()
    for root, _, files in os.walk(dwg_folder_path):
        for file_name in files:
            if file_name[-4:] != ".dwg":
                continue
            dwg_file_path = root + "/" + file_name
            save_file_path = dwg_file_path.replace(dwg_folder_path, save_folder_path)
            dwg_loader.openDWGFile(dwg_file_path)
            dwg_loader.saveAs(save_file_path)
    return True

