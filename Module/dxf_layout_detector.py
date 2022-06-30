#!/usr/bin/env python
# -*- coding: utf-8 -*-

import cv2
import numpy as np
from random import randint

from Data.shape import LineCluster

from Method.cross_check import getLineCrossLineListNum
from Method.cluster import clusterLine

from Module.dxf_renderer import DXFRenderer

class DXFLayoutDetector(DXFRenderer):
    def __init__(self):
        super(DXFLayoutDetector, self).__init__()

        self.valid_line_list = []
        self.valid_line_hv_only_list = []
        self.line_cluster_list = []
        self.outer_line_cluster = None
        return

    def updateValidLineList(self):
        self.valid_line_list = []

        for line in self.line_list:
            if line.isPoint():
                continue
            self.valid_line_list.append(line)
        return True

    def updateValidLineHVOnlyList(self):
        valid_k_list = [None, float("inf"), 0]
        k_0_error_max = 1e-6
        k_inf_min = 1e6

        self.valid_line_hv_only_list = []

        for valid_line in self.valid_line_list:
            line_k = valid_line.k
            if line_k not in valid_k_list:
                continue
            abs_line_k = abs(line_k)
            if k_0_error_max <= abs_line_k <= k_inf_min:
                continue
            self.valid_line_hv_only_list.append(valid_line)
        return True

    def clusterLines(self):
        line_list_list = clusterLine(self.valid_line_hv_only_list)
        for line_list in line_list_list:
            line_cluster = LineCluster(line_list)
            self.line_cluster_list.append(line_cluster)
        return True

    def updateOuterLineClusterByArea(self):
        self.outer_line_cluster = None

        max_bbox_area = 0
        for line_cluster in self.line_cluster_list:
            current_bbox_area = line_cluster.bbox.getArea()
            if current_bbox_area <= max_bbox_area:
                continue
            max_bbox_area = current_bbox_area
            self.outer_line_cluster = line_cluster
        return True

    def updateOuterLineClusterByLineNum(self):
        self.outer_line_cluster = None

        max_line_num = 0
        for line_cluster in self.line_cluster_list:
            current_line_num = len(line_cluster.line_list)
            if current_line_num <= max_line_num:
                continue
            max_line_num = current_line_num
            self.outer_line_cluster = line_cluster
        return True

    def updateOuterLineCluster(self):
        #  self.updateOuterLineClusterByArea()
        self.updateOuterLineClusterByLineNum()
        return True

    def detectLayout(self):
        self.circle_list = []
        self.updateBBox()

        if not self.updateValidLineList():
            print("[ERROR][DXFLayoutDetector::detectLayout]")
            print("\t updateValidLineList failed!")
            return False
        if not self.updateValidLineHVOnlyList():
            print("[ERROR][DXFLayoutDetector::detectLayout]")
            print("\t updateValidLineHVOnlyList failed!")
            return False
        if not self.clusterLines():
            print("[ERROR][DXFLayoutDetector::detectLayout]")
            print("\t clusterLines failed!")
            return False
        if not self.updateOuterLineCluster():
            print("[ERROR][DXFLayoutDetector::detectLayout]")
            print("\t updateOuterLineCluster failed!")
            return False
        return True

    def drawLineCluster(self):
        draw_white = True
        for line_cluster in self.line_cluster_list:
            random_color = [randint(0, 255),
                            randint(0, 255),
                            randint(0, 255)]
            if draw_white:
                random_color = [255, 255, 255]
                draw_white = False
            for line in line_cluster.line_list:
                start_point_in_image = self.getImagePosition(line.start_point)
                end_point_in_image = self.getImagePosition(line.end_point)
                cv2.line(self.image,
                         (start_point_in_image.x, start_point_in_image.y),
                         (end_point_in_image.x, end_point_in_image.y),
                         np.array(random_color, dtype=np.float) / 255.0,
                         1, 4)
        return True

    def drawOuterLineCluster(self):
        draw_color = [255, 255, 255]
        for line in self.outer_line_cluster.line_list:
            start_point_in_image = self.getImagePosition(line.start_point)
            end_point_in_image = self.getImagePosition(line.end_point)
            cv2.line(self.image,
                     (start_point_in_image.x, start_point_in_image.y),
                     (end_point_in_image.x, end_point_in_image.y),
                     np.array(draw_color, dtype=np.float) / 255.0,
                     1, 4)
        return True

    def drawShape(self):
        #  self.drawLineCluster()
        self.drawOuterLineCluster()
        self.drawArc()
        return True

def demo():
    dxf_file_path_dict = {
        "test1": "/home/chli/chLi/Download/DeepLearning/Dataset/CAD/test1.dxf",
        "1": "/home/chli/chLi/Download/DeepLearning/Dataset/CAD/给坤哥测试用例/户型图1.dxf",
        "2": "/home/chli/chLi/Download/DeepLearning/Dataset/CAD/给坤哥测试用例/户型图2.dxf",
        "3": "/home/chli/chLi/Download/DeepLearning/Dataset/CAD/给坤哥测试用例/户型图3.dxf",
        "4": "/home/chli/chLi/Download/DeepLearning/Dataset/CAD/给坤哥测试用例/户型图4.dxf",
        "5": "/home/chli/chLi/Download/DeepLearning/Dataset/CAD/给坤哥测试用例/户型图5.dxf",
        "6": "/home/chli/chLi/Download/DeepLearning/Dataset/CAD/给坤哥测试用例/户型图6.dxf",
        "7": "/home/chli/chLi/Download/DeepLearning/Dataset/CAD/给坤哥测试用例/户型图7.dxf",
        "8": "/home/chli/chLi/Download/DeepLearning/Dataset/CAD/给坤哥测试用例/户型图8.dxf",
        "9": "/home/chli/chLi/Download/DeepLearning/Dataset/CAD/给坤哥测试用例/户型图9.dxf",
        "10": "/home/chli/chLi/Download/DeepLearning/Dataset/CAD/给坤哥测试用例/户型图10.dxf",
    }

    dxf_file_path = dxf_file_path_dict["3"]
    debug = True
    image_width = 1600 * 1.2
    image_height = 900 * 1.2
    free_width = 50
    is_reverse_y = True
    wait_key = 0

    dxf_layout_detector = DXFLayoutDetector()
    dxf_layout_detector.loadFile(dxf_file_path)

    dxf_layout_detector.outputInfo(debug)

    dxf_layout_detector.detectLayout()

    dxf_layout_detector.setImageSize(image_width, image_height, free_width, is_reverse_y)
    dxf_layout_detector.render(wait_key)
    return True

if __name__ == "__main__":
    demo()

