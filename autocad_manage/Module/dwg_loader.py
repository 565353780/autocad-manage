#!/usr/bin/env python
# -*- coding: utf-8 -*-

#  import win32com.client
import comtypes.client

class DWGLoader(object):
    def __init__(self):
        self.autocad = None

        self.doc = None

        self.connectAutoCAD()
        return

    def connectAutoCAD(self):
        try:
            self.autocad = comtypes.client.GetActiveObject("AutoCAD.Application")
        except:
            print("[ERROR][DWGLoader::connectAutoCAD]")
            print("\t GetActiveObject failed! please start AutoCAD first!")
            return False

        self.autocad.Visible = True
        return True

    def openDWGFile(self, dwg_file_path):
        try:
            self.doc = self.autocad.Documents.Open(dwg_file_path)
        except:
            print("[ERROR][DWGLoader::openDWGFile]")
            print("\t Open failed! please check if file exist!")
            print("\t", dwg_file_path)
            return False
        return True

    def saveAs(self, save_file_path):
        return True

def demo():
    dwg_file_path = "L:/"
    save_file_path = "L:/"
    dwg_loader = DWGLoader()
    dwg_loader.openDWGFile(dwg_file_path)
    dwg_loader.saveAs(save_file_path)
    return True

def demo_folder():
    dwg_file_path = "L:/"
    save_file_path = "L:/"
    dwg_loader = DWGLoader()
    dwg_loader.openDWGFile(dwg_file_path)
    dwg_loader.saveAs(save_file_path)
    return True

