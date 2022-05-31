#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import cv2

from Module.dxf_loader import DXFLoader

class DXFRenderer(DXFLoader):
    def __init__(self):
        super(DXFRenderer, self).__init__()
        return

    def render(self):
        return True

def demo():
    dxf_file_path = "/home/chli/chLi/Download/DeepLearning/Dataset/CAD/test1.dxf"

    dxf_renderer = DXFRenderer()
    dxf_renderer.loadFile(dxf_file_path)
    dxf_renderer.render()

    #  dxf_renderer.outputInfo()
    return True

if __name__ == "__main__":
    demo()

