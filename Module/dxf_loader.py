#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import ezdxf

from Config.configs import RENDER_ALL

from Data.shape import Point, Line, Circle, Arc, BBox

class DXFLoader(object):
    def __init__(self, config):
        self.load_depth_dict = {
            "LWPOLYLINE" : -1,
            "INSERT" : 1,
        }

        self.config = config

        self.doc = None

        self.msp = None
        self.layout_names = []
        self.line_list = []
        self.circle_list = []
        self.arc_list = []
        self.bbox = BBox()
        self.undefined_entity_type_list = []

        self.loadFile(self.config['dxf_file_path'])
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

        start_point = Point(start[0], start[1], start[2])
        end_point = Point(end[0], end[1], end[2])

        # for 2-dim
        start_point.z = 0
        end_point.z = 0

        new_line = Line(start_point, end_point)
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

    def loadArcEntity(self, entity):
        dxf = entity.dxf
        dxftype = entity.dxftype()

        if dxftype != "ARC":
            print("[ERROR][DXFLoader::loadArcEntity]")
            print("\t this entity is a [" + dxftype + "], not a ARC!")
            return False


        center = dxf.center
        radius = dxf.radius
        start_angle = dxf.start_angle
        end_angle = dxf.end_angle

        flattening = entity.flattening(radius / 100)
        flatten_point_list = [Point(point[0], point[1], point[2]) for point in flattening]

        # for 2-dim
        for i in range(len(flatten_point_list)):
            flatten_point_list[i].z = 0

        new_arc = Arc(Point(center[0], center[1], center[2]), radius,
                      start_angle, end_angle, flatten_point_list)
        self.arc_list.append(new_arc)
        return True

    def loadEntity(self, entity, depth=0):
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

        if dxftype == "ARC":
            if not self.loadArcEntity(entity):
                print("[ERROR][DXFLoader::loadEntity]")
                print("\t loadArcEntity failed!")
                return False
            return True

        if dxftype in ["LWPOLYLINE", "INSERT"]:
            load_depth = self.load_depth_dict[dxftype]
            if depth >= load_depth and load_depth != -1:
                return True
            for virtual_entity in entity.virtual_entities():
                if not self.loadEntity(virtual_entity, depth + 1):
                    return False

        if dxftype in self.undefined_entity_type_list:
            return True

        self.undefined_entity_type_list.append(dxftype)
        print("[WARN][DXFLoader::loadEntity]")
        print("\t load algo for [" + dxftype + "] not defined!")
        return True

    def loadAllEntity(self):
        for entity in self.msp:
            self.loadEntity(entity)
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

        for arc in self.arc_list:
            if not self.bbox.addBBoxPosition(arc.bbox):
                print("[ERROR][DXFLoader::updateBBox]")
                print("\t addBBoxPosition for arc failed!")
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

        if dxftype == "ARC":
            if debug:
                return True
            print("center =", dxf.center)
            print("radius =", dxf.radius)
            print("start_angle =", dxf.start_angle)
            print("end_angle =", dxf.end_angle)
            return True

        if dxftype in ["LWPOLYLINE", "INSERT"]:
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

    def getShapeListLabelDict(self, shape_list):
        label_dict = {}
        for shape in shape_list:
            label = shape.getLabelStr()
            if label not in label_dict.keys():
                label_dict[label] = 1
                continue
            label_dict[label] += 1
        return label_dict

    def outputLabel(self):
        line_label_dict = self.getShapeListLabelDict(self.line_list)
        print("Line Label :")
        for key in line_label_dict.keys():
            print("\t", key, line_label_dict[key])

        circle_label_dict = self.getShapeListLabelDict(self.circle_list)
        print("Circle Label :")
        for key in circle_label_dict.keys():
            print("\t", key, circle_label_dict[key])

        arc_label_dict = self.getShapeListLabelDict(self.arc_list)
        print("Arc Label :")
        for key in arc_label_dict.keys():
            print("\t", key, arc_label_dict[key])
        return True

    def outputInfo(self):
        print("====entity====")
        self.outputEntity(self.config['debug'])

        print("====layout====")
        self.outputLayout()

        print("====query====")
        self.outputQuery()

        print("====block====")
        self.outputBlock()
        return True

def demo():
    config = RENDER_ALL

    dxf_loader = DXFLoader(config)
    dxf_loader.outputInfo()
    return True

if __name__ == "__main__":
    demo()

