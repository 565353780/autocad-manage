#!/usr/bin/env python
# -*- coding: utf-8 -*-

import cv2
import numpy as np
from random import randint

from Method.cluster import clusterLine

from Module.dxf_renderer import DXFRenderer

class DXFLayoutDetector(DXFRenderer):
    def __init__(self):
        super(DXFLayoutDetector, self).__init__()

        self.valid_line_list = []
        self.cluster_lines_list = []
        return

    def updateValidLineList(self):
        self.valid_line_list = []

        for line in self.line_list:
            if line.isPoint():
                continue
            self.valid_line_list.append(line)
        return True

    def clusterLines(self):
        if not self.updateValidLineList():
            print("[ERROR][DXFLayoutDetector::clusterLines]")
            print("\t updateValidLineList failed!")
            return False

        self.cluster_lines_list = clusterLine(self.valid_line_list)
        return True

    def drawClusterLine(self):
        draw_white = True
        for lines in self.cluster_lines_list:
            random_color = [randint(0, 255),
                            randint(0, 255),
                            randint(0, 255)]
            if draw_white:
                random_color = [255, 255, 255]
                draw_white = False
            for line in lines:
                start_point_in_image = self.getImagePosition(line.start_point)
                end_point_in_image = self.getImagePosition(line.end_point)
                cv2.line(self.image,
                         (start_point_in_image.x, start_point_in_image.y),
                         (end_point_in_image.x, end_point_in_image.y),
                         np.array(random_color, dtype=np.float) / 255.0,
                         1, 4)
        return True

    def drawShape(self):
        self.drawClusterLine()
        return True

def demo():
    dxf_file_path = "/home/chli/chLi/Download/DeepLearning/Dataset/CAD/test1.dxf"
    debug = True
    image_width = 1600 * 1.2
    image_height = 900 * 1.2
    free_width = 50
    wait_key = 0

    dxf_layout_detector = DXFLayoutDetector()
    dxf_layout_detector.loadFile(dxf_file_path)

    dxf_layout_detector.outputInfo(debug)

    dxf_layout_detector.clusterLines()

    dxf_layout_detector.setImageSize(image_width, image_height, free_width)
    #  dxf_layout_detector.render(wait_key)
    return True

if __name__ == "__main__":
    demo()

