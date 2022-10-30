#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import comtypes.client
from time import time
from tqdm import tqdm
from func_timeout import func_set_timeout
from pythoncom import CoInitialize, CoUninitialize

from autocad_manage.Config.path import TMP_SAVE_FOLDER_PATH

from autocad_manage.Method.path import createFileFolder, removeIfExist, renameFile


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

        CoInitialize()

        try:
            self.autocad = comtypes.client.GetActiveObject(
                "AutoCAD.Application")
        except:
            print("[ERROR][DWGLoader::connectAutoCAD]")
            print("\t GetActiveObject failed! please start AutoCAD first!")
            return False

        self.autocad.Visible = True
        return True

    def sendCMD(self, cmd, max_wait_second=30):
        self.connectAutoCAD()

        doc = None

        start = time()
        first_print = False
        while doc is None:
            try:
                doc = self.autocad.activedocument
            except:
                wait_second = time() - start
                if wait_second > max_wait_second:
                    print("[ERROR][DWGLoader::sendCMD]")
                    print("\t wait time out to select activedocument!")
                    CoUninitialize()
                    return False

                if first_print:
                    continue
                first_print = True
                print("[WARN][DWGLoader::sendCMD]")
                print("\t select activedocument failed! start retry...")

        start = time()
        first_print = False
        while True:
            try:
                doc.SendCommand(cmd)
            except:
                wait_second = time() - start
                if wait_second > max_wait_second:
                    print("[ERROR][DWGLoader::sendCMD]")
                    print("\t wait time out to send:")
                    print("\t", cmd)
                    CoUninitialize()
                    return False

                if first_print:
                    continue
                first_print = True
                print("[WARN][DWGLoader::sendCMD]")
                print("\t SendCommand failed! start retry...")
                print("\t", cmd)
                continue
            break

        CoUninitialize()
        return True

    @func_set_timeout(30)
    def callOpen(self, dwg_file_path):
        try:
            self.connectAutoCAD()
            self.doc = self.autocad.Documents.Open(dwg_file_path)
        except:
            print("[ERROR][DWGLoader::openDWGFile]")
            print("\t Open failed! please check if file exist!")
            print("\t", dwg_file_path)
            CoUninitialize()
            return False

        CoUninitialize()
        return True

    def openDWGFile(self, dwg_file_path):
        if not os.path.exists(dwg_file_path):
            print("[ERROR][DWGLoader::openDWGFile]")
            print("\t dwg_file not exist!")
            print("\t", dwg_file_path)
            return False

        try:
            if not self.callOpen(dwg_file_path):
                return False
        except:
            print("[ERROR][DWGLoader::openDWGFile]")
            print("\t callOpen time out!")
            print("\t", dwg_file_path)
            return False

        cmd = "FILEDIA " + "0\n"
        if not self.sendCMD(cmd):
            print("[ERROR][DWGLoader::openDWGFile]")
            print("\t set FILEDIA to 0 failed!")
            return False
        return True

    def fixError(self):
        cmd = "AUDIT " + "Y\n"
        if not self.sendCMD(cmd):
            print("[ERROR][DWGLoader::fixError]")
            print("\t sendCMD failed!")
            print("\t", cmd)
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

        cmd = "CLOSE\n"
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

        if not self.fixError():
            print("[ERROR][DWGLoader::transDwgToDxf]")
            print("\t fixError failed!")
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

    def transDwgFolderToDxf(self,
                            dwg_folder_path,
                            save_folder_path,
                            print_progress=False):
        file_path_pair_list = []
        for root, _, files in os.walk(dwg_folder_path):
            for file_name in files:
                if file_name[-4:] != ".dwg":
                    continue
                dwg_file_path = root + "/" + file_name
                save_file_path = \
                    root.replace(dwg_folder_path, save_folder_path) + "/" + \
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
                print("\t openDWGFile failed! skip this one!")
                print("\t", dwg_file_path)
                continue

            if not self.fixError():
                print("[ERROR][DWGLoader::transDwgFolderToDxf]")
                print("\t fixError failed!")
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
                continue
                #  return False

            if not renameFile(tmp_file_path, save_file_path):
                print("[ERROR][DWGLoader::transDwgFolderToDxf]")
                print("\t renameFile failed!")
                print("\t", tmp_file_path)
                print("\t ->")
                print("\t", save_file_path)
                return False
        return True
