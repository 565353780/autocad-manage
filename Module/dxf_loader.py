#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import ezdxf

from Data.shape import Point, Line, Circle

class DXFLoader(object):
    def __init__(self):
        self.doc = None

        self.msp = None
        self.layout_names = []
        self.line_list = []
        self.circle_list = []
        return

    def reset(self):
        self.doc = None
        self.msp = None
        self.layout_names = []
        self.line_list = []
        self.circle_list = []
        return True

    def loadLineEntity(self, entity):
        dxf = entity.dxf
        dxftype = entity.dxftype()

        if dxftype != "LINE":
            print("[ERROR][DXFLoader::loadLineEntity]")
            print("\t this entity is a [" + dxftype + "], not a LINE!")
            return False

        start = dxf.start
        end = dxf.end
        new_line = Line(Point(start[0], start[1], start[2]),
                        Point(end[0], end[1], end[2]))
        self.line_list.append(new_line)
        return True

    def loadCircleEntity(self, entity):
        dxf = entity.dxf
        dxftype = entity.dxftype()

        if dxftype != "CIRCLE":
            print("[ERROR][DXFLoader::loadCircleEntity]")
            print("\t this entity is a [" + dxftype + "], not a CIRCLE!")
            return False

        center = dxf.center
        radius = dxf.radius
        new_circle = Circle(Point(center[0], center[1], center[2]), radius)
        self.circle_list.append(new_circle)
        return True

    def loadEntity(self, entity):
        dxftype = entity.dxftype()

        if dxftype == "LINE":
            if not self.loadLineEntity(entity):
                print("[ERROR][DXFLoader::loadEntity]")
                print("\t loadLineEntity failed!")
                return False
            return True

        if dxftype == "CIRCLE":
            if not self.loadCircleEntity(entity):
                print("[ERROR][DXFLoader::loadEntity]")
                print("\t loadCircleEntity failed!")
                return False
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

    def outputInfo(self):
        print("====entity====")
        self.outputEntity()

        print("====layout====")
        self.outputLayout()

        print("====query====")
        self.outputQuery()

        print("====block====")
        self.outputBlock()
        return True

def demo():
    dxf_file_path = "/home/chli/chLi/Download/DeepLearning/Dataset/CAD/test1.dxf"

    dxf_loader = DXFLoader()
    dxf_loader.loadFile(dxf_file_path)

    #  dxf_loader.outputInfo()
    return True

if __name__ == "__main__":
    demo()

