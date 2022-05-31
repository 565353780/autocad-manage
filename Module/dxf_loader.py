#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import ezdxf

from Data.point import Point
from Data.line import Line

class DXFLoader(object):
    def __init__(self):
        self.doc = None

        self.msp = None
        self.layout_names = None
        self.line_list = None
        return

    def reset(self):
        self.doc = None
        self.msp = None
        self.layout_names = None
        self.line_list = None
        return True

    def loadEntity(self, entity):
        dxf = entity.dxf
        dxftype = entity.dxftype()

        if dxftype == "LINE":
            start = dxf.start
            end = dxf.end
            new_line = Line(Point(start[0], start[1], start[2]),
                            Point(end[0], end[1], end[2]))
            self.line_list.append(new_line)
            return True
        print("[WARN][DXFLoader::loadEntity]")
        print("\t load algo for [" + dxftype + "] not defined!")
        return False

    def loadAllEntity(self):
        for entity in self.msp:
            if not self.loadEntity(entity):
                print("[WARN][DXFLoader::loadAllEntity]")
                print("\t loadEntity failed!")
                continue
        return True

    def loadFile(self, dxf_file_path):
        self.reset()

        if not os.path.exists(dxf_file_path):
            print("[ERROR][DXFLoader::loadFile]")
            print("\t dxf file not exist!")
            return False

        self.doc = ezdxf.readfile(dxf_file_path)
        self.msp = self.doc.modelspace()
        self.layout_names = self.doc.layout_names()
        self.line_list = []

        if not self.loadAllEntity():
            print("[ERROR][DXFLoader::loadFile]")
            print("\t loadAllEntity failed!")
            return False
        return True

    def print_entity(self, entity):
        print()

        dxf = entity.dxf
        dxftype = entity.dxftype()

        print("dxftype =", dxftype)
        print("layer =", dxf.layer)
        print("color =", dxf.color)

        if dxftype == "LINE":
            print("start:", dxf.start)
            print("end:", dxf.end)
            return True
        if dxftype == "CIRCLE":
            print("center =", dxf.center)
            print("radius =", dxf.radius)
            return True

        print("[WARN][demo::print_entity]")
        print("print algo for this type not exist!")
        return False

    def outputEntity(self):
        print("entity num =", len(self.msp))
        for entity in self.msp:
            self.print_entity(entity)

        #  for entity in self.msp.query("LINE"):
            #  print_entity(entity)
        return True

    def outputLayout(self):
        print("layout_names =", self.layout_names)
        layout_list = []
        for layout_name in self.layout_names:
            layout_list.append(self.doc.layout(layout_name))
        return True

    def outputQuery(self):
        lines = self.msp.query('LINE[layer=="Model"]')
        return True

    def outputBlock(self):
        print("block num =", len(self.doc.blocks))
        for b in self.doc.blocks:
            break
        return True

def demo():
    dxf_file_path = "/home/chli/chLi/Download/DeepLearning/Dataset/CAD/test1.dxf"

    dxf_loader = DXFLoader()
    dxf_loader.loadFile(dxf_file_path)

    print("====entity====")
    dxf_loader.outputEntity()

    print("====layout====")
    dxf_loader.outputLayout()

    print("====query====")
    dxf_loader.outputQuery()

    print("====block====")
    dxf_loader.outputBlock()
    return True

if __name__ == "__main__":
    demo()

