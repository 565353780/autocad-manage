#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
sys.path.append("../method-manage")

import os
import comtypes.client
#  import win32com.client
from tqdm import tqdm

from method_manage.Config.path import TMP_SAVE_FOLDER_PATH

from method_manage.Method.path import createFileFolder, removeIfExist, renameFile

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

        first_print = False
        while doc is None:
            try:
                doc = self.autocad.activedocument
            except:
                if first_print:
                    continue
                first_print = True
                print("[WARN][DWGLoader::sendCMD]")
                print("\t select activedocument failed! start retry...")

        first_print = False
        while True:
            try:
                doc.SendCommand(cmd)
            except:
                if first_print:
                    continue
                first_print = True
                print("[WARN][DWGLoader::sendCMD]")
                print("\t SendCommand failed! start retry...")
                print("\t", cmd)
            break
        return True

    def openDWGFile(self, dwg_file_path):
        if not os.path.exists(dwg_file_path):
            print("[ERROR][DWGLoader::openDWGFile]")
            print("\t dwg_file not exist!")
            print("\t", dwg_file_path)
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

        cmd = "SAVEAS "

        if save_file_path[-4:] == ".dxf":
            cmd += "dxf " + "16 " + save_file_path + "\n"
        elif save_file_path[-4:] == ".dwg":
            cmd += "2018 " + save_file_path + "\n"
        else:
            print("[ERROR][DWGLoader::saveAs]")
            print("\t save_file format not valid!")
            return False

        if not self.sendCMD(cmd):
            print("[ERROR][DWGLoader::saveAs]")
            print("\t sendCMD failed!")
            print("\t", cmd)
            return False
        return True

    def closeDoc(self):
        tmp_file_path = TMP_SAVE_FOLDER_PATH + "tmp.dwg"
        removeIfExist(tmp_file_path)

        if not self.saveAs(tmp_file_path):
            print("[ERROR][DWGLoader::closeDoc]")
            print("\t saveAs dwg failed!")
            return False

        cmd = "CLOSE "
        if not self.sendCMD(cmd):
            print("[ERROR][DWGLoader::closeDoc]")
            print("\t sendCMD failed!")
            print("\t", cmd)
            return False

        removeIfExist(tmp_file_path)
        return True

    def transDwgToDxf(self, dwg_file_path, save_file_path):
        tmp_file_path = save_file_path[:-4] + "_tmp.dxf"

        if not self.openDWGFile(dwg_file_path):
            print("[ERROR][DWGLoader::transDwgToDxf]")
            print("\t openDWGFile failed!")
            print("\t", dwg_file_path)
            return False

        if not self.saveAs(tmp_file_path):
            print("[ERROR][DWGLoader::transDwgToDxf]")
            print("\t saveAs failed!")
            print("\t", tmp_file_path)
            return False

        if not self.closeDoc():
            print("[ERROR][DWGLoader::transDwgToDxf]")
            print("\t closeDoc failed!")
            print("\t", dwg_file_path)
            return False

        if not os.path.exists(tmp_file_path):
            print("[ERROR][DWGLoader::transDwgToDxf]")
            print("\t save dxf file failed!")
            return False

        if not renameFile(tmp_file_path, save_file_path):
            print("[ERROR][DWGLoader::transDwgToDxf]")
            print("\t renameFile failed!")
            print("\t", tmp_file_path)
            print("\t ->")
            print("\t", save_file_path)
            return False
        return True

    def transDwgFolderToDxf(self, dwg_folder_path, save_folder_path, print_progress=False):
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

        for_data = file_path_pair_list
        if print_progress:
            print("[INFO][DWGLoader::transDwgFolderToDxf]")
            print("\t start save as dxf files...")
            for_data = tqdm(for_data)
        for file_path_pair in for_data:
            dwg_file_path, save_file_path = file_path_pair

            if os.path.exists(save_file_path):
                continue

            tmp_file_path = save_file_path[:-4] + "_tmp.dxf"

            if not self.openDWGFile(dwg_file_path):
                print("[ERROR][DWGLoader::transDwgFolderToDxf]")
                print("\t openDWGFile failed!")
                print("\t", dwg_file_path)
                return False

            if not self.saveAs(tmp_file_path):
                print("[ERROR][DWGLoader::transDwgFolderToDxf]")
                print("\t saveAs failed!")
                print("\t", tmp_file_path)
                return False

            if not self.closeDoc():
                print("[ERROR][DWGLoader::transDwgFolderToDxf]")
                print("\t closeDoc failed!")
                print("\t", dwg_file_path)
                return False

            if not os.path.exists(tmp_file_path):
                print("[ERROR][DWGLoader::transDwgFolderToDxf]")
                print("\t save dxf file failed!")
                return False

            if not renameFile(tmp_file_path, save_file_path):
                print("[ERROR][DWGLoader::transDwgFolderToDxf]")
                print("\t renameFile failed!")
                print("\t", tmp_file_path)
                print("\t ->")
                print("\t", save_file_path)
                return False
        return True

def demo():
    dwg_file_path = \
        "L:/CAD/House_1/20210223/C00000103/1e9a1ce8f2104613bfa4882cff473c42.dwg"
    save_file_path = \
        "L:/CAD/output/DXF/House_1/20210223/C00000103/1e9a1ce8f2104613bfa4882cff473c42.dxf"

    dwg_loader = DWGLoader()
    dwg_loader.transDwgToDxf(dwg_file_path, save_file_path)
    return True

def demo_folder():
    dwg_folder_path = "L:/CAD/House_1/"
    save_folder_path = "L:/CAD/DXF/House_1/"

    dwg_loader = DWGLoader()
    dwg_loader.transDwgFolderToDxf(dwg_folder_path, save_folder_path, True)
    return True

