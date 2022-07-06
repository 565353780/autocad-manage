#!/usr/bin/env python
# -*- coding: utf-8 -*-

import numpy as np
from cv2 import waitKey

from Config.configs import CONFIG_COLLECTION

from Data.line import Line
from Data.line_cluster import LineCluster

from Method.cross_check import \
    isPointCrossLineList, getPointCrossLineListNum, isPointInArcArea, \
    isLineHorizontal, isLineVertical, isLineParallel, isLineListOnSameLines, \
    isLineListCross, isLineCrossArcList
from Method.similar_check import isHaveSameLine
from Method.connect_check import isLineListConnectInAllLineList, isLineListUniform
from Method.cluster import clusterLineByCross, clusterLineBySimilar
from Method.dists import getPointDist2, getPointDist, getLineDist, getLineDist2
from Method.labels import \
    getShapeListWithLabel, getShapeListWithAnyLabelList, getShapeListDictWithLabel

from Module.dxf_renderer import DXFRenderer

class DXFLayoutDetector(DXFRenderer):
    def __init__(self, config):
        super(DXFLayoutDetector, self).__init__(config)

        self.detectLayout()
        return

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

    def updateCabinetForValidLine(self):
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

        selected_line_length_max = np.max(selected_line_length_pair_list)
        length_min = selected_line_length_max / 10.0

        cabinet_idx = 0
        for idx_pair, length_pair in zip(selected_line_idx_pair_list, selected_line_length_pair_list):
            if min(length_pair) < length_min:
                continue
            line_list[idx_pair[0]].setLabel("MaybeCabinet", cabinet_idx)
            line_list[idx_pair[1]].setLabel("MaybeCabinet", cabinet_idx)
            cabinet_idx += 1
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
        self.circle_list = []
        self.updateBBox()

        if not self.updateValidForLine():
            print("[ERROR][DXFLayoutDetector::detectLayout]")
            print("\t updateValidForLine failed!")
            return False
        if not self.updateHVForValidLine():
            print("[ERROR][DXFLayoutDetector::detectLayout]")
            print("\t updateHVForValidLine failed!")
            return False
        if not self.updateCabinetForValidLine():
            print("[ERROR][DXFLayoutDetector::detectLayout]")
            print("\t updateCabinetForValidLine failed!")
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

        self.outputLabel([
            "Valid",
            "Horizontal", "Vertical",
            "Unit", "UnitCrossCluster",
            "Layout", "LayoutCrossCluster",
            "SingleConnect",
        ])
        return True

    def drawShape(self):
        self.drawLineLabel("ConnectLayout", [255, 255, 255])
        self.drawArcLabel("Door", [0, 0, 255])
        self.drawLineLabel("Door", [0, 0, 255])
        self.drawLineLabel("UniformDistWindow", [0, 255, 0])

        self.drawLineLabel("MaybeCabinet", [255, 0, 0])
        return True

def demo_with_edit_config(config, kv_list):
    for k, v in kv_list:
        config[k] = v
    dxf_layout_detector = DXFLayoutDetector(config)
    dxf_layout_detector.render()
    return True

def demo_debug():
    config = CONFIG_COLLECTION['3']

    renderer = DXFRenderer(config)
    renderer.render()

    demo_with_edit_config(config, [['window_name', 'detect']])
    waitKey(0)
    return True

def demo():
    config = CONFIG_COLLECTION['test1']

    dxf_layout_detector = DXFLayoutDetector(config)
    dxf_layout_detector.outputInfo()
    dxf_layout_detector.render()
    waitKey(0)
    return True

if __name__ == "__main__":
    demo()

