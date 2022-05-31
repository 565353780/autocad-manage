#!/usr/bin/env python
# -*- coding: utf-8 -*-

import ezdxf

def print_entity(e):
    print()

    dxf = e.dxf
    dxftype = e.dxftype()

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

dxf_file_path = "/home/chli/chLi/Download/DeepLearning/Dataset/CAD/test1.dxf"

doc = ezdxf.readfile(dxf_file_path)

print("====entities====")
msp = doc.modelspace()
for e in msp:
    print_entity(e)

#  for e in msp.query("LINE"):
    #  print_entity(e)

