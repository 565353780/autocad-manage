#!/usr/bin/env python
# -*- coding: utf-8 -*-

from Module.dxf_renderer import DXFRenderer

class DXFLayoutDetector(DXFRenderer):
    def __init__(self):
        super(DXFLayoutDetector, self).__init__()
        return

def demo():
    dxf_file_path = "/home/chli/chLi/Download/DeepLearning/Dataset/CAD/test1.dxf"
    image_width = 1600
    image_height = 900
    free_width = 50

    dxf_layout_detector = DXFLayoutDetector()
    dxf_layout_detector.loadFile(dxf_file_path)
    dxf_layout_detector.setImageSize(image_width, image_height, free_width)
    dxf_layout_detector.render()

    #  dxf_layout_detector.outputInfo()
    return True

if __name__ == "__main__":
    demo()

