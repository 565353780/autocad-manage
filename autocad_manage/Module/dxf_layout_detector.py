#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import numpy as np
from tqdm import tqdm
from cv2 import waitKey

from method_manage.Method.path import renameFile

from autocad_manage.Config.base_config import BASE_CONFIG

from autocad_manage.Data.line import Line
from autocad_manage.Data.line_cluster import LineCluster

from autocad_manage.Method.cross_check import \
    getPointCrossLineListNum, isPointInArcArea, \
    isLineHorizontal, isLineVertical, isLineParallel, \
    isLineListOnSameLines, isLineListCross, isLineCrossArcList
from autocad_manage.Method.similar_check import isHaveSameLine
from autocad_manage.Method.connect_check import \
    isLineListConnectInAllLineList, isLineConnectInLineList, isLineListUniform
from autocad_manage.Method.cluster import clusterLineByCross, clusterLineBySimilar
from autocad_manage.Method.dists import getPointDist2, getPointDist, getLineDist2, getMinDistWithLineIdx
from autocad_manage.Method.labels import \
    getShapeListWithLabel, getShapeListWithAnyLabelList, getShapeListDictWithLabel

from autocad_manage.Module.dxf_renderer import DXFRenderer

class DXFLayoutDetector(DXFRenderer):
    def __init__(self, dxf_file_path=None, config=BASE_CONFIG):
        super(DXFLayoutDetector, self).__init__(dxf_file_path, config)

        if dxf_file_path is not None:
            self.detectLayout()
        return

    def reset(self):
        super().reset()
        return True

    def updateValidForLine(self):
        for line in self.line_list:
            if line.isPoint():
                continue
            line.setLabel("Valid")
        return True

    def updateHVForValidLine(self):
        k_0_max = self.config['k_0_max']
        k_inf_min = self.config['k_inf_min']

        line_list = getShapeListWithLabel(self.line_list, "Valid")

        for line in line_list:
            if isLineHorizontal(line, k_0_max):
                line.setLabel("Horizontal")
                continue

            if isLineVertical(line, k_inf_min):
                line.setLabel("Vertical")
        return True

    def updateCabinetForValidWithoutHVLine(self):
        cabinet_angle_error_max = 10

        line_list = getShapeListWithLabel(self.line_list, "Valid", None, ["Horizontal", "Vertical"])

        selected_line_idx_pair_list = []
        selected_line_length_pair_list = []
        for i in range(len(line_list) - 1):
            if i in selected_line_idx_pair_list:
                continue

            abs_angle_1 = abs(line_list[i].getAngle())
            if abs_angle_1 < cabinet_angle_error_max or \
                    abs_angle_1 > 90 - cabinet_angle_error_max:
                continue

            length_1 = line_list[i].getLength()

            middle_point_1 = line_list[i].getMiddlePoint()
            for j in range(i + 1, len(line_list)):
                if j in selected_line_idx_pair_list:
                    continue

                abs_angle_2 = abs(line_list[j].getAngle())
                if abs_angle_2 < cabinet_angle_error_max or \
                        abs_angle_2 > 90 - cabinet_angle_error_max:
                    continue

                if abs(abs_angle_1 - abs_angle_2) > self.config['angle_error_max']:
                    continue

                length_2 = line_list[j].getLength()
                if abs(length_1 - length_2) > self.config['dist_error_max']:
                    continue

                middle_point_2 = line_list[j].getMiddlePoint()
                point_dist = getPointDist(middle_point_1, middle_point_2)
                if point_dist > self.config['dist_error_max']:
                    continue

                selected_line_idx_pair_list.append([i, j])
                selected_line_length_pair_list.append([length_1, length_2])

        if len(selected_line_length_pair_list) == 0:
            return True

        selected_line_length_max = np.max(selected_line_length_pair_list)
        length_min = selected_line_length_max / 10.0

        cabinet_idx = 0
        for idx_pair, length_pair in zip(selected_line_idx_pair_list, selected_line_length_pair_list):
            if min(length_pair) < length_min:
                continue
            line_list[idx_pair[0]].setLabel("Cabinet", cabinet_idx)
            line_list[idx_pair[1]].setLabel("Cabinet", cabinet_idx)
            cabinet_idx += 1
        return True

    def updateCabinetBBoxForHVLine(self):
        line_list_dict = getShapeListDictWithLabel(self.line_list, "Cabinet")

        line_list = getShapeListWithAnyLabelList(self.line_list, ["Horizontal", "Vertical"])

        for key, cabinet_line_list in line_list_dict.items():
            line_cluster = LineCluster(cabinet_line_list)
            bound_point_list = line_cluster.bbox.getBoundPointList()
            bound_line_list = [
                Line(bound_point_list[0], bound_point_list[1]),
                Line(bound_point_list[0], bound_point_list[2]),
                Line(bound_point_list[1], bound_point_list[3]),
                Line(bound_point_list[2], bound_point_list[3])]

            for bound_line in bound_line_list:
                if not isLineConnectInLineList(bound_line, line_list):
                    continue

                min_dist, min_dist_idx = getMinDistWithLineIdx(bound_line, line_list)
                if min_dist > self.config['dist_error_max'] * 10:
                    break

                line_list[min_dist_idx].setLabel("CabinetBBox", int(key))
        return True

    def updateUnitAndRepeatForHVLine(self):
        hv_line_list = getShapeListWithAnyLabelList(self.line_list, ["Horizontal", "Vertical"])
        unit_line_list = []
        repeat_line_list = []
        for line in hv_line_list:
            if isHaveSameLine(line, unit_line_list, self.config['dist_error_max'] * 10):
                repeat_line_list.append(line)
            else:
                unit_line_list.append(line)

        for line in unit_line_list:
            line.setLabel("Unit")

        for line in repeat_line_list:
            line.setLabel("Repeat")
        return True

    def updateCrossClusterForUnitLine(self):
        cluster_label_list = ["Unit"]
        if not clusterLineByCross(self.line_list,
                                  cluster_label_list,
                                  "UnitCrossCluster",
                                  self.config['dist_error_max']):
            print("[ERROR][DXFLayoutDetector::updateCrossClusterForUnitLine]")
            print("\t clusterLineByCross failed!")
        return True

    def getMaxAreaLineListFromCluster(self, cluster_label):
        max_area_line_list = []

        line_list_dict = getShapeListDictWithLabel(self.line_list, cluster_label)

        max_bbox_area = 0
        for key in line_list_dict.keys():
            line_list = line_list_dict[key]
            current_bbox_area = LineCluster(line_list).bbox.getArea()
            if current_bbox_area <= max_bbox_area:
                continue
            max_bbox_area = current_bbox_area
            max_area_line_list = line_list
        return max_area_line_list

    def getMaxSizeLineListFromCluster(self, cluster_label):
        max_size_line_list = []

        line_list_dict = getShapeListDictWithLabel(self.line_list, cluster_label)

        max_line_num = 0
        for key in line_list_dict.keys():
            line_list = line_list_dict[key]
            current_line_num = len(line_list)
            if current_line_num <= max_line_num:
                continue
            max_line_num = current_line_num
            max_size_line_list = line_list
        return max_size_line_list

    def updateMaybeLayoutForCrossClusterLine(self):
        #  layout_line_list = self.getMaxAreaLineListFromCluster("UnitCrossCluster")
        layout_line_list = self.getMaxSizeLineListFromCluster("UnitCrossCluster")

        for layout_line in layout_line_list:
            layout_line.setLabel("MaybeLayout")
        return True

    def updateMaybeDoorForArc(self):
        error_max = 40

        max_radius = 0
        door_arc_list = []
        for arc in self.arc_list:
            angles = abs(arc.end_angle - arc.start_angle)
            angles_error = min(abs(angles - 90), abs(angles - 270))
            if angles_error <= error_max:
                door_arc_list.append(arc)
                max_radius = max(max_radius, arc.radius)

        radius_min = 0.5 * max_radius
        for arc in door_arc_list:
            if arc.radius < radius_min:
                continue
            arc.setLabel("MaybeDoor")
        return True

    def updateLayoutAndSingleConnectForMaybeLayoutLine(self):
        single_connect_removed_line_list = getShapeListWithLabel(self.line_list, "MaybeLayout")
        last_line_list = []

        door_arc_list = getShapeListWithLabel(self.arc_list, "MaybeDoor")

        find_single_connect_line = True
        while find_single_connect_line:
            find_single_connect_line = False

            last_line_list = single_connect_removed_line_list
            single_connect_removed_line_list = []

            for line in last_line_list:
                if isLineCrossArcList(line , door_arc_list, self.config['dist_error_max']):
                    single_connect_removed_line_list.append(line)
                    continue

                start_point_cross_line_num = getPointCrossLineListNum(
                    line.start_point, last_line_list, self.config['dist_error_max'] * 100)
                if start_point_cross_line_num < 2:
                    find_single_connect_line = True
                    line.start_point.setLabel("SingleConnect")
                    line.setLabel("SingleConnect")
                    continue

                end_point_cross_line_num = getPointCrossLineListNum(
                    line.end_point, last_line_list, self.config['dist_error_max'] * 100)
                if end_point_cross_line_num < 2:
                    find_single_connect_line = True
                    line.end_point.setLabel("SingleConnect")
                    line.setLabel("SingleConnect")
                    continue

                single_connect_removed_line_list.append(line)

        for line in single_connect_removed_line_list:
            line.setLabel("Layout")

        for line in self.line_list:
            line.removeLabel("MaybeLayout", True)
        return True

    def updateLayoutCrossClusterForLayoutLine(self):
        cluster_label_list = ["Layout"]
        if not clusterLineByCross(self.line_list,
                                  cluster_label_list,
                                  "LayoutCrossCluster",
                                  self.config['dist_error_max']):
            print("[ERROR][DXFLayoutDetector::updateLayoutCrossClusterForLayoutLine]")
            print("\t clusterLineByCross failed!")
        return True

    def updateConnectLayoutForLayoutCrossClusterLine(self):
        #  layout_line_list = self.getMaxAreaLineListFromCluster("LayoutCrossCluster")
        layout_line_list = self.getMaxSizeLineListFromCluster("LayoutCrossCluster")

        for layout_line in layout_line_list:
            layout_line.setLabel("ConnectLayout")
        return True

    def updateDoorForConnectLayoutLine(self):
        dist_error_max = self.config['dist_error_max']
        angle_error_max = self.config['angle_error_max']
        k_0_max = self.config['k_0_max']
        k_inf_min = self.config['k_inf_min']

        arc_line_pair_list = []

        door_arc_list = getShapeListWithLabel(self.arc_list, "MaybeDoor")
        for arc in door_arc_list:
            center = arc.center
            start_point = arc.flatten_point_list[0]
            end_point = arc.flatten_point_list[-1]
            start_line = Line(center, start_point)
            end_line = Line(center, end_point)
            arc_line_pair_list.append([start_line, end_line])

        line_list = getShapeListWithLabel(self.line_list, "ConnectLayout")

        valid_door_arc_list = []
        door_line_pair_pair_list = []
        for door_arc, arc_line_pair in zip(door_arc_list, arc_line_pair_list):
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

                is_first_line_hv = isLineHorizontal(first_min_dist_line, k_0_max) or \
                    isLineVertical(first_min_dist_line, k_inf_min)
                is_second_line_hv = isLineHorizontal(second_min_dist_line, k_0_max) or \
                    isLineVertical(second_min_dist_line, k_inf_min)

                if not is_first_line_hv or not is_second_line_hv:
                    continue

                if not isLineParallel(first_min_dist_line, second_min_dist_line, angle_error_max):
                    continue

                if not isLineParallel(arc_line, first_min_dist_line, angle_error_max) and \
                        not isLineParallel(arc_line, second_min_dist_line, angle_error_max):
                    continue

                point_dist_s = getPointDist(first_min_dist_line.start_point, arc_line.end_point)
                point_dist_e = getPointDist(first_min_dist_line.end_point, arc_line.end_point)
                point_min_dist = min(point_dist_s, point_dist_e)
                if point_min_dist > dist_error_max:
                    continue

                door_line_pair_pair.append([line_list[first_line_idx], line_list[second_line_idx]])

            if len(door_line_pair_pair) == 0:
                continue

            valid_door_arc_list.append(door_arc)
            door_line_pair_pair_list.append(door_line_pair_pair)

        door_arc_list = valid_door_arc_list

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

        door_idx = 0
        for arc, door_line_pair_pair in zip(door_arc_list, door_line_pair_pair_list):
            arc.setLabel("Door", door_idx)
            for door_line_pair in door_line_pair_pair:
                for door_line in door_line_pair:
                    door_line.setLabel("Door", door_idx)
            door_idx += 1

        for arc in self.arc_list:
            arc.removeLabel("MaybeDoor", True)
        return True

    def updateSimilarClusterIdxForConnectLayoutLine(self):
        cluster_label_list = ["ConnectLayout"]
        if not clusterLineBySimilar(self.line_list,
                                    cluster_label_list,
                                    "LayoutSimilarCluster",
                                    self.config['length_error_ratio_max'],
                                    self.config['angle_error_max'],
                                    self.config['dist_error_max']):
            print("[ERROR][DXFLayoutDetector::updateSimilarClusterIdxForConnectLayoutLine]")
            print("\t clusterLineBySimilar failed!")
        return True

    def updateMaybeWindowForSimilarClusterLine(self):
        window_line_num_min = self.config['window_line_num_min']
        window_line_num_max = self.config['window_line_num_max']

        similar_cluster_dict = getShapeListDictWithLabel(self.line_list, "LayoutSimilarCluster")

        window_idx = 0
        for _, line_list in similar_cluster_dict.items():
            if len(line_list) < window_line_num_min or len(line_list) > window_line_num_max:
                continue
            for line in line_list:
                line.setLabel("MaybeWindow", window_idx)
            window_idx += 1

        for line in self.line_list:
            line.removeLabel("LayoutSimilarCluster", True)
        return True

    def updateNoCrossWindowForMaybeWindowLine(self):
        maybe_window_dict = getShapeListDictWithLabel(self.line_list, "MaybeWindow")

        cross_window_key_list = []
        merge_key_list_list = []
        for key_1, line_list_1 in maybe_window_dict.items():
            if key_1 in cross_window_key_list:
                continue

            find_cross_line_list = False
            for key_2, line_list_2 in maybe_window_dict.items():
                if key_1 == key_2:
                    continue
                if key_2 in cross_window_key_list:
                    continue
                if not isLineListCross(line_list_1, line_list_2):
                    continue
                if isLineListOnSameLines(line_list_1, line_list_2,
                                         self.config['angle_error_max'],
                                         self.config['dist_error_max']):
                    key_merged = False
                    for i in range(len(merge_key_list_list)):
                        merge_key_list = merge_key_list_list[i]
                        if key_1 not in merge_key_list and key_2 not in merge_key_list:
                            continue

                        if key_1 in merge_key_list:
                            if key_2 in merge_key_list:
                                key_merged = True
                                break
                            merge_key_list_list[i].append(key_2)
                            key_merged = True
                            break

                        if key_2 in merge_key_list:
                            merge_key_list_list[i].append(key_1)
                            key_merged = True
                            break

                    if not key_merged:
                        merge_key_list_list.append([key_1, key_2])
                    continue
                cross_window_key_list.append(key_2)
                find_cross_line_list = True

            if find_cross_line_list:
                cross_window_key_list.append(key_1)

        merged_maybe_window_dict = {}
        for key, window_line_list in maybe_window_dict.items():
            key_need_to_merge = False
            key_in_merge_list = None
            for merge_key_list in merge_key_list_list:
                if key in merge_key_list:
                    key_need_to_merge = True
                    key_in_merge_list = merge_key_list
                    break

            if not key_need_to_merge:
                merged_maybe_window_dict[key] = window_line_list
                continue

            find_saved_key = False
            for merge_key in key_in_merge_list:
                if merge_key in merged_maybe_window_dict:
                    merged_maybe_window_dict[merge_key] += window_line_list
                    find_saved_key = True
                    break

            if not find_saved_key:
                merged_maybe_window_dict[key] = window_line_list

        window_idx = 0
        for key, line_list in merged_maybe_window_dict.items():
            if key in cross_window_key_list:
                continue
            for line in line_list:
                line.setLabel("NoCrossWindow", window_idx)
            window_idx += 1

        for line in self.line_list:
            line.removeLabel("MaybeWindow", True)
        return True

    def updateConnectAndDisconnectWindowForNoCrossWindowLine(self):
        layout_line_list = getShapeListWithLabel(self.line_list, "ConnectLayout")
        no_cross_window_dict = getShapeListDictWithLabel(self.line_list, "NoCrossWindow")

        connect_window_idx = 0
        disconnect_window_idx = 0
        for _, window_line_list in no_cross_window_dict.items():
            if isLineListConnectInAllLineList(window_line_list, layout_line_list,
                                              self.config['dist_error_max']):
                for line in window_line_list:
                    line.setLabel("ConnectWindow", connect_window_idx)
                connect_window_idx += 1
                continue
            for line in window_line_list:
                line.setLabel("DisconnectWindow", disconnect_window_idx)
            disconnect_window_idx += 1
        return True

    def updateUniformAndRandomDistWindowForConnectWindowLine(self):
        connect_window_dict = getShapeListDictWithLabel(self.line_list, "ConnectWindow")

        uniform_dist_window_idx = 0
        random_dist_window_idx = 0
        for _, connect_window_line_list in connect_window_dict.items():
            if isLineListUniform(connect_window_line_list, self.config['uniform_dist_var_min']):
                for line in connect_window_line_list:
                    line.setLabel("UniformDistWindow", uniform_dist_window_idx)
                uniform_dist_window_idx += 1
                continue
            for line in connect_window_line_list:
                line.setLabel("RandomDistWindow", random_dist_window_idx)
            random_dist_window_idx += 1
        return True

    def detectLayout(self):
        self.updateBBox()

        if not self.updateValidForLine():
            print("[ERROR][DXFLayoutDetector::detectLayout]")
            print("\t updateValidForLine failed!")
            return False
        if not self.updateHVForValidLine():
            print("[ERROR][DXFLayoutDetector::detectLayout]")
            print("\t updateHVForValidLine failed!")
            return False
        if not self.updateCabinetForValidWithoutHVLine():
            print("[ERROR][DXFLayoutDetector::detectLayout]")
            print("\t updateCabinetForValidWithoutHVLine failed!")
            return False
        if not self.updateCabinetBBoxForHVLine():
            print("[ERROR][DXFLayoutDetector::detectLayout]")
            print("\t updateCabinetBBoxForHVLine failed!")
            return False
        if not self.updateUnitAndRepeatForHVLine():
            print("[ERROR][DXFLayoutDetector::detectLayout]")
            print("\t updateUnitAndRepeatForHVLine failed!")
            return False
        if not self.updateCrossClusterForUnitLine():
            print("[ERROR][DXFLayoutDetector::detectLayout]")
            print("\t updateCrossClusterForUnitLine failed!")
            return False
        if not self.updateMaybeLayoutForCrossClusterLine():
            print("[ERROR][DXFLayoutDetector::detectLayout]")
            print("\t updateMaybeLayoutForCrossClusterLine failed!")
            return False
        if not self.updateMaybeDoorForArc():
            print("[ERROR][DXFLayoutDetector::detectLayout]")
            print("\t updateMaybeDoorForArc failed!")
            return False
        if not self.updateLayoutAndSingleConnectForMaybeLayoutLine():
            print("[ERROR][DXFLayoutDetector::detectLayout]")
            print("\t updateLayoutAndSingleConnectForMaybeLayoutLine failed!")
            return False
        if not self.updateLayoutCrossClusterForLayoutLine():
            print("[ERROR][DXFLayoutDetector::detectLayout]")
            print("\t updateLayoutCrossClusterForLayoutLine failed!")
            return False
        if not self.updateConnectLayoutForLayoutCrossClusterLine():
            print("[ERROR][DXFLayoutDetector::detectLayout]")
            print("\t updateConnectLayoutForLayoutCrossClusterLine failed!")
            return False
        if not self.updateDoorForConnectLayoutLine():
            print("[ERROR][DXFLayoutDetector::detectLayout]")
            print("\t updateDoorForConnectLayoutLine failed!")
            return False
        if not self.updateSimilarClusterIdxForConnectLayoutLine():
            print("[ERROR][DXFLayoutDetector::detectLayout]")
            print("\t updateSimilarClusterIdxForConnectLayoutLine failed!")
            return False
        if not self.updateMaybeWindowForSimilarClusterLine():
            print("[ERROR][DXFLayoutDetector::detectLayout]")
            print("\t updateWindowForLayoutLine failed!")
            return False
        if not self.updateNoCrossWindowForMaybeWindowLine():
            print("[ERROR][DXFLayoutDetector::detectLayout]")
            print("\t updateNoCrossWindowForMaybeWindowLine failed!")
            return False
        if not self.updateConnectAndDisconnectWindowForNoCrossWindowLine():
            print("[ERROR][DXFLayoutDetector::detectLayout]")
            print("\t updateConnectAndDisconnectWindowForNoCrossWindowLine failed!")
            return False
        if not self.updateUniformAndRandomDistWindowForConnectWindowLine():
            print("[ERROR][DXFLayoutDetector::detectLayout]")
            print("\t updateUniformAndRandomDistWindowForConnectWindowLine failed!")
            return False

        #  self.outputLabel([
            #  "Valid",
            #  "Horizontal", "Vertical",
            #  "Cabinet", "CabinetBBox",
            #  "Unit", "UnitCrossCluster",
            #  "Layout", "LayoutCrossCluster",
            #  "SingleConnect",
        #  ])

        return True

    def drawShape(self):
        self.drawLineLabel("ConnectLayout", [255, 255, 255])

        self.drawArcLabel("Door", [0, 0, 255])
        self.drawLineLabel("Door", [0, 0, 255])

        self.drawLineLabel("Cabinet", [255, 255, 0])
        self.drawLineLabel("CabinetBBox", [255, 255, 0])

        self.drawLineLabel("UniformDistWindow", [0, 255, 0])
        return True

    def transDxfToJsonWithLayout(self,
                                 dxf_file_path,
                                 save_json_file_path,
                                 save_image_file_path=None,
                                 compare_with_all_shape=False):
        if not self.loadFile(dxf_file_path):
            print("[ERROR][DXFLayoutDetector::transDxfToJsonWithLayout]")
            print("\t loadFile failed!")
            print("\t", dxf_file_path)
            return False

        if not self.detectLayout():
            print("[ERROR][DXFLayoutDetector::transDxfToJsonWithLayout]")
            print("\t detectLayout failed!")
            print("\t", dxf_file_path)
            return False

        if save_image_file_path is not None:
            if not self.saveImage(save_image_file_path, compare_with_all_shape):
                print("[ERROR][DXFLayoutDetector::transDxfToJsonWithLayout]")
                print("\t saveImage failed!")
                print("\t", save_image_file_path)
                return False

        tmp_file_path = save_json_file_path[:-5] + "_tmp.json"

        if not self.saveJson(tmp_file_path):
            print("[ERROR][DXFLayoutDetector::transDxfToJsonWithLayout]")
            print("\t saveJson failed!")
            print("\t", tmp_file_path)
            return False

        if not os.path.exists(tmp_file_path):
            print("[ERROR][DXFLayoutDetector::transDxfToJsonWithLayout]")
            print("\t trans dxf to json failed!")
            print("\t", dxf_file_path)
            return False

        if not renameFile(tmp_file_path, save_json_file_path):
            print("[ERROR][DXFLayoutDetector::transDxfToJsonWithLayout]")
            print("\t renameFile failed!")
            print("\t", tmp_file_path)
            print("\t ->")
            print("\t", save_json_file_path)
            return False
        return True

    def transDxfFolderToJsonWithLayout(self,
                                       dxf_folder_path,
                                       save_json_folder_path,
                                       save_image_folder_path=None,
                                       compare_with_all_shape=False,
                                       print_progress=False):
        file_path_pair_list = []
        for root, _, files in os.walk(dxf_folder_path):
            for file_name in files:
                if file_name[-4:] != ".dxf":
                    continue
                dxf_file_path = root + "/" + file_name
                save_json_file_path = \
                    root.replace(dxf_folder_path, save_json_folder_path) + "/" + \
                    file_name[:-4] + ".json"
                save_image_file_path = None
                if save_image_folder_path is not None:
                    save_image_file_path = \
                        root.replace(dxf_folder_path, save_image_folder_path) + "/" + \
                        file_name[:-4] + ".png"
                file_path_pair_list.append([dxf_file_path, save_json_file_path, save_image_file_path])

        for_data = file_path_pair_list
        if print_progress:
            print("[INFO][DXFLayoutDetector::transDxfFolderToJsonWithLayout]")
            print("\t start trans dxf to json...")
            for_data = tqdm(file_path_pair_list)
        for file_path_list in for_data:
            dxf_file_path, save_json_file_path, save_image_file_path = file_path_list

            if os.path.exists(save_json_file_path):
                continue

            tmp_file_path = save_json_file_path[:-5] + "_tmp.json"

            if not self.loadFile(dxf_file_path):
                print("[INFO][DXFLayoutDetector::transDxfFolderToJsonWithLayout]")
                print("\t loadFile failed!")
                print("\t", dxf_file_path)
                return False

            if not self.detectLayout():
                print("[INFO][DXFLayoutDetector::transDxfFolderToJsonWithLayout]")
                print("\t detectLayout failed!")
                return False

            if save_image_file_path is not None:
                if not self.saveImage(save_image_file_path, compare_with_all_shape):
                    print("[INFO][DXFLayoutDetector::transDxfFolderToJsonWithLayout]")
                    print("\t saveImage failed!")
                    print("\t", save_image_file_path)
                    return False

            if not self.saveJson(tmp_file_path):
                print("[INFO][DXFLayoutDetector::transDxfFolderToJsonWithLayout]")
                print("\t saveJson failed!")
                print("\t", tmp_file_path)
                return False

            if not os.path.exists(tmp_file_path):
                print("[INFO][DXFLayoutDetector::transDxfFolderToJsonWithLayout]")
                print("\t trans dxf to json failed!")
                return False

            if not renameFile(tmp_file_path, save_json_file_path):
                print("[INFO][DXFLayoutDetector::transDxfFolderToJsonWithLayout]")
                print("\t renameFile failed!")
                return False
        return True

def demo():
    dxf_file_path = "/home/chli/chLi/CAD/DXF/户型识别文件/1.dxf"
    save_json_file_path = "/home/chli/chLi/CAD/JSON/户型识别文件/1.json"
    save_image_file_path = "/home/chli/chLi/CAD/Image/户型识别文件/1.png"
    compare_with_all_shape = True

    dxf_layout_detector = DXFLayoutDetector(dxf_file_path)
    dxf_layout_detector.outputInfo()
    dxf_layout_detector.saveImage(save_image_file_path, compare_with_all_shape)
    dxf_layout_detector.render()
    waitKey(0)
    dxf_layout_detector.saveJson(save_json_file_path)
    return True

def demo_trans():
    dxf_file_path = "/home/chli/chLi/CAD/DXF/户型识别文件/1.dxf"
    save_json_file_path = "/home/chli/chLi/CAD/JSON/户型识别文件/1.json"
    save_image_file_path = "/home/chli/chLi/CAD/Image/户型识别文件/1.png"
    compare_with_all_shape = True

    dxf_layout_detector = DXFLayoutDetector()
    dxf_layout_detector.transDxfToJsonWithLayout(
        dxf_file_path,
        save_json_file_path,
        save_image_file_path,
        compare_with_all_shape
    )
    return True

def demo_trans_folder():
    dxf_folder_path = "/home/chli/chLi/CAD/DXF/House_1/"
    save_json_folder_path = "/home/chli/chLi/CAD/JSON/House_1/"
    save_image_folder_path = "/home/chli/chLi/CAD/Image/House_1/"
    compare_with_all_shape = True
    print_progress = True

    dxf_layout_detector = DXFLayoutDetector()
    dxf_layout_detector.transDxfFolderToJsonWithLayout(
        dxf_folder_path,
        save_json_folder_path,
        save_image_folder_path,
        compare_with_all_shape,
        print_progress
    )
    return True

