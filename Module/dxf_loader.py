#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import ezdxf

from Data.shape import Point, Line, Circle, BBox

class DXFLoader(object):
    def __init__(self):
        self.doc = None

        self.msp = None
        self.layout_names = []
        self.line_list = []
        self.circle_list = []
        self.bbox = BBox()
        self.undefined_entity_type_list = []
        return

    def reset(self):
        self.doc = None
        self.msp = None
        self.layout_names = []
        self.line_list = []
        self.circle_list = []
        self.bbox = BBox()
        self.undefined_entity_type_list = []
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

    def loadLWPolyLineEntity(self, entity):
        dxftype = entity.dxftype()

        if dxftype != "LWPOLYLINE":
            print("[ERROR][DXFLoader::loadLWPolyLineEntity]")
            print("\t this entity is a [" + dxftype + "], not a LWPOLYLINE!")
            return False

        for virtual_entity in entity.virtual_entities():
            virtual_dxftype = virtual_entity.dxftype()

            if virtual_dxftype == "LINE":
                if not self.loadLineEntity(virtual_entity):
                    print("[ERROR][DXFLoader::loadLWPolyLineEntity]")
                    print("\t this entity is a [" + dxftype + "], not a LINE!")
                    return False
                continue

            if virtual_dxftype == "CIRCLE":
                if not self.loadCircleEntity(virtual_entity):
                    print("[ERROR][DXFLoader::loadLWPolyLineEntity]")
                    print("\t this entity is a [" + dxftype + "], not a CIRCLE!")
                    return False
                continue

            if dxftype in self.undefined_entity_type_list:
                continue

            self.undefined_entity_type_list.append(dxftype)
            print("[ERROR][DXFLoader::loadLWPolyLineEntity]")
            print("\t load algo for [" + dxftype + "] not defined!")
        return True

    def loadInsertEntity(self, entity):
        dxftype = entity.dxftype()

        if dxftype != "INSERT":
            print("[ERROR][DXFLoader::loadInsertEntity]")
            print("\t this entity is a [" + dxftype + "], not a INSERT!")
            return False

        for virtual_entity in entity.virtual_entities():
            virtual_dxftype = virtual_entity.dxftype()

            if virtual_dxftype == "LINE":
                if not self.loadLineEntity(virtual_entity):
                    print("[ERROR][DXFLoader::loadInsertEntity]")
                    print("\t this entity is a [" + dxftype + "], not a LINE!")
                    return False
                continue

            if virtual_dxftype == "CIRCLE":
                if not self.loadCircleEntity(virtual_entity):
                    print("[ERROR][DXFLoader::loadInsertEntity]")
                    print("\t this entity is a [" + dxftype + "], not a CIRCLE!")
                    return False
                continue

            if dxftype in self.undefined_entity_type_list:
                continue

            self.undefined_entity_type_list.append(dxftype)
            print("[ERROR][DXFLoader::loadInsertEntity]")
            print("\t load algo for [" + dxftype + "] not defined!")
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

        if dxftype == "LWPOLYLINE":
            print("found LWPOLYLINE")
            if not self.loadLWPolyLineEntity(entity):
                print("[ERROR][DXFLoader::loadEntity]")
                print("\t loadLWPolyLineEntity failed!")
                return False
            return True

        if dxftype == "INSERT":
            if not self.loadInsertEntity(entity):
                print("[ERROR][DXFLoader::loadEntity]")
                print("\t loadInsertEntity failed!")
                return False
            return True

        if dxftype in self.undefined_entity_type_list:
            return False

        self.undefined_entity_type_list.append(dxftype)
        print("[WARN][DXFLoader::loadEntity]")
        print("\t load algo for [" + dxftype + "] not defined!")
        return False

    def loadAllEntity(self):
        for entity in self.msp:
            if not self.loadEntity(entity):
                #  print("[WARN][DXFLoader::loadAllEntity]")
                #  print("\t loadEntity failed!")
                continue
        return True

    def updateBBox(self):
        self.bbox.reset()

        for line in self.line_list:
            if not self.bbox.addBBoxPosition(line.bbox):
                print("[ERROR][DXFLoader::updateBBox]")
                print("\t addBBoxPosition for line failed!")
                return False

        for circle in self.circle_list:
            if not self.bbox.addBBoxPosition(circle.bbox):
                print("[ERROR][DXFLoader::updateBBox]")
                print("\t addBBoxPosition for circle failed!")
                return False
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

        if not self.updateBBox():
            print("[ERROR][DXFLoader::loadFile]")
            print("\t updateBBox failed!")
            return False
        return True

    def print_entity(self, entity, debug=False):
        if not debug:
            print()

        dxf = entity.dxf
        dxftype = entity.dxftype()

        if not debug:
            print("dxftype =", dxftype)
            print("layer =", dxf.layer)
            print("color =", dxf.color)

        if dxftype == "LINE":
            if debug:
                return True
            print("start:", dxf.start)
            print("end:", dxf.end)
            return True
        if dxftype == "CIRCLE":
            if debug:
                return True
            print("center =", dxf.center)
            print("radius =", dxf.radius)
            return True
        if dxftype == "LWPOLYLINE":
            for entity in entity.virtual_entities():
                self.print_entity(entity, debug)
        if dxftype == "INSERT":
            for entity in entity.virtual_entities():
                self.print_entity(entity, debug)

        if dxftype in self.undefined_entity_type_list:
            return False

        self.undefined_entity_type_list.append(dxftype)
        print("[WARN][demo::print_entity]")
        print("print algo for this type [" + dxftype + "] not exist!")
        return False

    def outputEntity(self, debug=False):
        print("entity num =", len(self.msp))

        for entity in self.msp:
            self.print_entity(entity, debug)

        #  for entity in self.msp.query("LINE"):
            #  self.print_entity(entity, True)

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

    def outputInfo(self, debug=False):
        print("====entity====")
        self.outputEntity(debug)

        print("====layout====")
        self.outputLayout()

        print("====query====")
        self.outputQuery()

        print("====block====")
        self.outputBlock()
        return True

def demo():
    dxf_file_path = "/home/chli/chLi/Download/DeepLearning/Dataset/CAD/test1.dxf"
    debug = True

    dxf_loader = DXFLoader()
    dxf_loader.loadFile(dxf_file_path)

    dxf_loader.outputInfo(debug)
    return True

if __name__ == "__main__":
    demo()

