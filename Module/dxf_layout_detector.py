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
        self.line_cluster_list = []
        self.outer_line_cluster = None
        self.outer_line_hv_only_cluster = None
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

        line_list_list = clusterLine(self.valid_line_list)
        for line_list in line_list_list:
            line_cluster = LineCluster(line_list)
            self.line_cluster_list.append(line_cluster)
        return True

    def updateOuterLineCluster(self):
        self.outer_line_cluster = None

        max_bbox_area = 0
        for line_cluster in self.line_cluster_list:
            current_bbox_area = line_cluster.bbox.getArea()
            if current_bbox_area <= max_bbox_area:
                continue
            max_bbox_area = current_bbox_area
            self.outer_line_cluster = line_cluster
        return True

    def updateOuterLineHVOnlyCluster(self):
        valid_k_list = [None, float("inf"), 0]
        k_0_error_max = 1e-6
        k_inf_min = 1e6

        remove_line_idx_list = []
        remove_line_list = []

        outer_line_list = self.outer_line_cluster.line_list
        for i in range(len(outer_line_list)):
            line_k = outer_line_list[i].k
            if line_k in valid_k_list:
                continue
            abs_line_k = abs(line_k)
            if abs_line_k < k_0_error_max or abs_line_k > k_inf_min:
                continue
            remove_line_idx_list.append(i)
            remove_line_list.append(outer_line_list[i])

        #  for i in range(len(outer_line_list)):
            #  if i in remove_line_idx_list:
                #  continue
            #  line_cross_line_list_num = \
                #  getLineCrossLineListNum(outer_line_list[i], remove_line_list)
            #  if line_cross_line_list_num < 1:
                #  continue
            #  remove_line_idx_list.append(i)
            
        self.outer_line_hv_only_cluster = LineCluster()
        for i in range(len(outer_line_list)):
            if i in remove_line_idx_list:
                continue
            self.outer_line_hv_only_cluster.addLine(outer_line_list[i])
        return True

    def detectLayout(self):
        if not self.clusterLines():
            print("[ERROR][DXFLayoutDetector::detectLayout]")
            print("\t clusterLines failed!")
            return False
        if not self.updateOuterLineCluster():
            print("[ERROR][DXFLayoutDetector::detectLayout]")
            print("\t updateOuterLineCluster failed!")
            return False
        if not self.updateOuterLineHVOnlyCluster():
            print("[ERROR][DXFLayoutDetector::detectLayout]")
            print("\t updateOuterLineHVOnlyCluster failed!")
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

    def drawOuterLineHVOnlyCluster(self):
        draw_color = [255, 255, 255]
        for line in self.outer_line_hv_only_cluster.line_list:
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
        #  self.drawOuterLineCluster()
        self.drawOuterLineHVOnlyCluster()
        return True

def demo():
    dxf_file_path = "/home/chli/chLi/Download/DeepLearning/Dataset/CAD/test1.dxf"
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

