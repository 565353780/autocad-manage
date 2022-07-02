#!/usr/bin/env python
# -*- coding: utf-8 -*-

import cv2
import numpy as np
from random import randint

from Config.configs import \
    LAYOUT_TEST1, LAYOUT_3, LAYOUT_4, LAYOUT_5, \
    LAYOUT_6, LAYOUT_9, LAYOUT_10

from Data.line import Line

from Method.cross_check import isLineParallel, isPointInArcArea
from Method.cluster import clusterLineByIdx
from Method.dists import getPointDist2, getLineDist2

from Module.dxf_renderer import DXFRenderer

class DXFLayoutDetector(DXFRenderer):
    def __init__(self, config):
        super(DXFLayoutDetector, self).__init__(config)

        self.line_cluster_list = []
        self.outer_line_cluster = None
        self.door_arc_list = []
        self.door_line_list = []
        self.door_removed_line_cluster = None

        self.detectLayout()
        return

    def updateValidLine(self):
        for line in self.line_list:
            if line.isPoint():
                continue
            line.setLabel("Valid")
        return True

    def updateValidLineHVOnly(self):
        valid_k_list = [float("inf"), 0]
        k_0_error_max = 1e-6
        k_inf_min = 1e6

        for line in self.line_list:
            valid_label = line.getLabel("Valid")
            if valid_label is None:
                continue
            line_k = line.k
            if line_k in valid_k_list:
                if line_k == 0:
                    line.setLabel("Horizontal")
                    continue
                line.setLabel("Vertical")
                continue
            abs_line_k = abs(line_k)
            if abs_line_k < k_0_error_max:
                line.setLabel("Horizontal")
                continue
            if abs_line_k > k_inf_min:
                line.setLabel("Vertical")
        return True

    def clusterLines(self):
        cluster_label_list = ["Horizontal", "Vertical"]
        self.line_cluster_list = clusterLineByIdx(self.line_list,
                                                  cluster_label_list,
                                                  self.config['max_dist_error'])
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

    def updateDoorArcList(self):
        error_max = 10

        max_radius = 0
        min_radius = float('inf')
        door_arc_list = []
        for arc in self.arc_list:
            angles = abs(arc.end_angle - arc.start_angle)
            if abs(angles - 90) <= error_max:
                door_arc_list.append(arc)
                max_radius = max(max_radius, arc.radius)
                min_radius = min(min_radius, arc.radius)

        mean_radius = (max_radius + min_radius) / 2.0

        for arc in door_arc_list:
            if arc.radius < mean_radius:
                continue
            self.door_arc_list.append(arc)
        return True

    def updateDoorLineList(self):
        angle_error_max = 10.0

        arc_line_pair_list = []

        for arc in self.door_arc_list:
            center = arc.center
            start_point = arc.flatten_point_list[0]
            end_point = arc.flatten_point_list[-1]
            start_line = Line(center, start_point)
            end_line = Line(center, end_point)
            arc_line_pair_list.append([start_line, end_line])

        line_list = self.outer_line_cluster.line_list

        valid_door_arc_list = []
        door_line_pair_pair_list = []
        for door_arc, arc_line_pair in zip(self.door_arc_list, arc_line_pair_list):
            door_line_pair_pair = []
            for arc_line in arc_line_pair:
                first_line_idx = -1
                second_line_idx = -1
                first_min_dist_to_arc_line = float('inf')
                second_min_dist_to_arc_line = float('inf')
                for i, line in enumerate(line_list):
                    current_dist_to_door_line = getLineDist2(arc_line, line)
                    if current_dist_to_door_line >= second_min_dist_to_arc_line:
                        continue

                    second_line_idx = i
                    second_min_dist_to_arc_line = current_dist_to_door_line

                    if current_dist_to_door_line >= first_min_dist_to_arc_line:
                        continue

                    second_line_idx = first_line_idx
                    second_min_dist_to_arc_line = first_min_dist_to_arc_line
                    first_line_idx = i
                    first_min_dist_to_arc_line = current_dist_to_door_line
                first_min_dist_line = line_list[first_line_idx]
                second_min_dist_line = line_list[second_line_idx]

                if not isLineParallel(arc_line, first_min_dist_line, angle_error_max) or \
                        not isLineParallel(arc_line, second_min_dist_line, angle_error_max):
                    continue

                door_line_pair_pair.append([line_list[first_line_idx], line_list[second_line_idx]])

            if len(door_line_pair_pair) == 0:
                continue

            valid_door_arc_list.append(door_arc)
            door_line_pair_pair_list.append(door_line_pair_pair)

        self.door_arc_list = valid_door_arc_list

        extra_door_line_list = []
        for valid_door_arc, door_line_pair_pair in \
                zip(valid_door_arc_list, door_line_pair_pair_list):
            for door_line_pair in door_line_pair_pair:
                arc_line = door_line_pair[0]
                second_min_dist_line = door_line_pair[1]

                arc_line_start_point_to_center_dist = \
                    getPointDist2(arc_line.start_point, valid_door_arc.center)
                arc_line_end_point_to_center_dist = \
                    getPointDist2(arc_line.end_point, valid_door_arc.center)

                arc_line_point = arc_line.start_point
                if arc_line_end_point_to_center_dist > arc_line_start_point_to_center_dist:
                    arc_line_point = arc_line.end_point

                door_line_start_point_to_arc_line_point_dist = \
                    getPointDist2(second_min_dist_line.start_point, arc_line_point)
                door_line_end_point_to_arc_line_point_dist = \
                    getPointDist2(second_min_dist_line.end_point, arc_line_point)

                door_line_point = second_min_dist_line.start_point
                if door_line_end_point_to_arc_line_point_dist < \
                        door_line_start_point_to_arc_line_point_dist:
                    door_line_point = second_min_dist_line.end_point

                if isPointInArcArea(door_line_point, valid_door_arc):
                    extra_door_line_list.append(Line(arc_line_point, door_line_point))

        self.door_line_list = []
        for door_line_pair_pair in door_line_pair_pair_list:
            for door_line_pair in door_line_pair_pair:
                self.door_line_list += door_line_pair

        self.door_line_list += extra_door_line_list
        return True

    def updateDoorRemovedLineCluster(self):
        return True

    def detectLayout(self):
        self.circle_list = []
        self.updateBBox()

        if not self.updateValidLine():
            print("[ERROR][DXFLayoutDetector::detectLayout]")
            print("\t updateValidLine failed!")
            return False
        if not self.updateValidLineHVOnly():
            print("[ERROR][DXFLayoutDetector::detectLayout]")
            print("\t updateValidLineHVOnly failed!")
            return False
        if not self.clusterLines():
            print("[ERROR][DXFLayoutDetector::detectLayout]")
            print("\t clusterLines failed!")
            return False
        if not self.updateOuterLineCluster():
            print("[ERROR][DXFLayoutDetector::detectLayout]")
            print("\t updateOuterLineCluster failed!")
            return False
        if not self.updateDoorArcList():
            print("[ERROR][DXFLayoutDetector::detectLayout]")
            print("\t updateDoorArcList failed!")
            return False
        if not self.updateDoorLineList():
            print("[ERROR][DXFLayoutDetector::detectLayout]")
            print("\t updateDoorLineList failed!")
            return False
        if not self.updateDoorRemovedLineCluster():
            print("[ERROR][DXFLayoutDetector::detectLayout]")
            print("\t updateDoorRemovedLineCluster failed!")
            return False
        return True

    def drawLabel(self, label):
        value_color_dict = {}
        for line in self.line_list:
            value = line.getLabel(label)
            if value is None:
                continue
            if value not in value_color_dict.keys():
                random_color = [randint(0, 255),
                                randint(0, 255),
                                randint(0, 255)]
                value_color_dict[value] = random_color
            color = value_color_dict[value]
            start_point_in_image = self.getImagePosition(line.start_point)
            end_point_in_image = self.getImagePosition(line.end_point)
            cv2.line(self.image,
                     (start_point_in_image.x, start_point_in_image.y),
                     (end_point_in_image.x, end_point_in_image.y),
                     np.array(color, dtype=np.float) / 255.0,
                     1, 4)
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

    def drawDoorArcList(self):
        for arc in self.door_arc_list:
            point_list = arc.flatten_point_list
            for i in range(len(point_list) - 1):
                current_point = point_list[i]
                next_point = point_list[i + 1]
                current_point_in_image = self.getImagePosition(current_point)
                next_point_in_image = self.getImagePosition(next_point)
                cv2.line(self.image,
                         (current_point_in_image.x, current_point_in_image.y),
                         (next_point_in_image.x, next_point_in_image.y),
                         np.array(self.arc_color, dtype=np.float) / 255.0,
                         1, 4)
        return True

    def drawDoorLineList(self):
        draw_color = [0, 0, 255]
        for line in self.door_line_list:
            start_point_in_image = self.getImagePosition(line.start_point)
            end_point_in_image = self.getImagePosition(line.end_point)
            cv2.line(self.image,
                     (start_point_in_image.x, start_point_in_image.y),
                     (end_point_in_image.x, end_point_in_image.y),
                     np.array(draw_color, dtype=np.float) / 255.0,
                     1, 4)
        return True

    def drawDoorRemovedLineCluster(self):
        draw_color = [255, 0, 255]
        for line in self.door_removed_line_cluster.line_list:
            start_point_in_image = self.getImagePosition(line.start_point)
            end_point_in_image = self.getImagePosition(line.end_point)
            cv2.line(self.image,
                     (start_point_in_image.x, start_point_in_image.y),
                     (end_point_in_image.x, end_point_in_image.y),
                     np.array(draw_color, dtype=np.float) / 255.0,
                     1, 4)
        return True

    def drawShape(self):

        #  self.drawLabel("Horizontal")
        #  self.drawLabel("Vertical")
        #  return True

        #  self.drawLabel("Cluster")
        #  return True

        #  self.drawLineCluster()
        self.drawOuterLineCluster()

        self.drawDoorArcList()
        self.drawDoorLineList()
        #  self.drawDoorRemovedLineCluster()
        return True

def demo_with_edit_config(config, kv_list):
    for k, v in kv_list:
        config[k] = v
    dxf_layout_detector = DXFLayoutDetector(config)
    dxf_layout_detector.render()
    return True

def demo_debug():
    config = LAYOUT_TEST1

    renderer = DXFRenderer(config)
    renderer.render()

    #  demo_with_edit_config(config, [['window_name', 'detect']])
    demo_with_edit_config(config, [['max_dist_error', 0], ['window_name', 'err_0']])
    cv2.waitKey(0)
    return True

def demo():
    config = LAYOUT_TEST1

    dxf_layout_detector = DXFLayoutDetector(config)
    dxf_layout_detector.outputInfo()
    dxf_layout_detector.render()
    cv2.waitKey(0)
    return True

if __name__ == "__main__":
    demo()

