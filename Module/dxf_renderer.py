#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import cv2

from Module.dxf_loader import DXFLoader

class DXFRenderer(DXFLoader):
    def __init__(self):
        super.__init__(self)
        return

    def render(self):
        return True

def demo():
    dxf_file_path = "/home/chli/chLi/Download/DeepLearning/Dataset/CAD/test1.dxf"

    dxf_renderer = DXFRenderer()
    dxf_renderer.loadFile(dxf_file_path)

    print("====entity====")
    dxf_renderer.loadAllEntity()
    dxf_renderer.getEntity()

    print("====layout====")
    dxf_renderer.getLayout()

    print("====query====")
    dxf_renderer.getQuery()

    print("====block====")
    dxf_renderer.getBlock()
    return True

if __name__ == "__main__":
    demo()

