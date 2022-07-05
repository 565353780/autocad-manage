#!/usr/bin/env python
# -*- coding: utf-8 -*-

from cv2 import waitKey

from Config.configs import CONFIG_COLLECTION

from Data.line import Line
from Data.line_cluster import LineCluster

from Method.cross_check import \
    isLineHorizontal, isLineVertical, \
    isLineParallel, isPointInArcArea, \
    getPointCrossLineListNum
from Method.cluster import \
    clusterLineByCross, clusterLineBySimilar
from Method.dists import getPointDist2, getLineDist2
from Method.labels import \
    getShapeListWithLabel, getShapeListDictWithLabel

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

        for line in self.line_list:
            valid_label = line.getLabel("Valid")
            if valid_label is None:
                continue

            if isLineHorizontal(line, k_0_max):
                line.setLabel("Horizontal")
                continue

            if isLineVertical(line, k_inf_min):
                line.setLabel("Vertical")
        return True

    def updateCrossClusterIdxForHVLine(self):
        cluster_label_list = ["Horizontal", "Vertical"]
        if not clusterLineByCross(self.line_list,
                                  cluster_label_list,
                                  self.config['dist_error_max']):
            print("[ERROR][DXFLayoutDetector::updateCrossClusterIdxForHVLine]")
            print("\t clusterLineByCross failed!")
        return True

    def getMaybeLayoutLineListFromCrossClusterByArea(self):
        layout_line_list = []

        line_list_dict = getShapeListDictWithLabel(self.line_list, "CrossCluster")

        max_bbox_area = 0
        for key in line_list_dict.keys():
            line_list = line_list_dict[key]
            current_bbox_area = LineCluster(line_list).bbox.getArea()
            if current_bbox_area <= max_bbox_area:
                continue
            max_bbox_area = current_bbox_area
            layout_line_list = line_list
        return layout_line_list

    def getMaybeLayoutLineListFromCrossClusterLineNum(self):
        layout_line_list = []

        line_list_dict = getShapeListDictWithLabel(self.line_list, "CrossCluster")

        max_line_num = 0
        for key in line_list_dict.keys():
            line_list = line_list_dict[key]
            current_line_num = len(line_list)
            if current_line_num <= max_line_num:
                continue
            max_line_num = current_line_num
            layout_line_list = line_list
        return layout_line_list

    def updateMaybeLayoutForCrossClusterLine(self):
        #  layout_line_list = self.getMaybeLayoutLineListFromCrossClusterByArea()
        layout_line_list = self.getMaybeLayoutLineListFromCrossClusterLineNum()

        for layout_line in layout_line_list:
            layout_line.setLabel("MaybeLayout")
        return True

    def updateLayoutAndSingleConnectForMaybeLayoutLine(self):
        single_connect_removed_line_list = getShapeListWithLabel(self.line_list, "MaybeLayout")
        last_line_list = []

        find_single_connect_line = True
        while find_single_connect_line:
            find_single_connect_line = False

            last_line_list = single_connect_removed_line_list
            single_connect_removed_line_list = []

            for line in last_line_list:
                start_point_cross_line_num = getPointCrossLineListNum(
                    line.start_point, last_line_list, self.config['dist_error_max'] * 1000)
                if start_point_cross_line_num < 2:
                    find_single_connect_line = True
                    line.start_point.setLabel("SingleConnect")
                    line.setLabel("SingleConnect")
                    continue

                end_point_cross_line_num = getPointCrossLineListNum(
                    line.end_point, last_line_list, self.config['dist_error_max'] * 1000)
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

    def updateDoorForLayoutLine(self):
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

        line_list = getShapeListWithLabel(self.line_list, "Layout")

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

    def updateSimilarClusterIdxForLayoutLine(self):
        cluster_label_list = ["Layout"]
        if not clusterLineBySimilar(self.line_list,
                                    cluster_label_list,
                                    self.config['length_error_ratio_max'],
                                    self.config['angle_error_max'],
                                    self.config['dist_error_max']):
            print("[ERROR][DXFLayoutDetector::updateSimilarClusterIdxForLayoutLine]")
            print("\t clusterLineBySimilar failed!")
        return True

    def updateWindowForSimilarClusterLine(self):
        similar_cluster_dict = getShapeListDictWithLabel(self.line_list, "SimilarCluster")

        window_idx = 0
        for _, item in similar_cluster_dict.items():
            if len(item) < 3:
                continue
            for line in item:
                line.setLabel("MaybeWindow", window_idx)
            window_idx += 1

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
        if not self.updateCrossClusterIdxForHVLine():
            print("[ERROR][DXFLayoutDetector::detectLayout]")
            print("\t updateCrossClusterIdxForHVLine failed!")
            return False
        if not self.updateMaybeLayoutForCrossClusterLine():
            print("[ERROR][DXFLayoutDetector::detectLayout]")
            print("\t updateMaybeLayoutForCrossClusterLine failed!")
            return False
        if not self.updateLayoutAndSingleConnectForMaybeLayoutLine():
            print("[ERROR][DXFLayoutDetector::detectLayout]")
            print("\t updateLayoutAndSingleConnectForMaybeLayoutLine failed!")
            return False
        if not self.updateMaybeDoorForArc():
            print("[ERROR][DXFLayoutDetector::detectLayout]")
            print("\t updateMaybeDoorForArc failed!")
            return False
        if not self.updateDoorForLayoutLine():
            print("[ERROR][DXFLayoutDetector::detectLayout]")
            print("\t updateDoorForLayoutLine failed!")
            return False
        if not self.updateSimilarClusterIdxForLayoutLine():
            print("[ERROR][DXFLayoutDetector::detectLayout]")
            print("\t updateSimilarClusterIdxForLayoutLine failed!")
            return False
        if not self.updateWindowForSimilarClusterLine():
            print("[ERROR][DXFLayoutDetector::detectLayout]")
            print("\t updateWindowForLayoutLine failed!")
            return False

        self.outputLabel(["Valid", "Horizontal", "Vertical",
                          "CrossCluster", "SimilarCluster"])
        return True

    def drawShape(self):
        self.drawLineList(getShapeListWithLabel(self.line_list, "Layout"), [255, 255, 255])

        self.drawArcList(getShapeListWithLabel(self.arc_list, "Door"), [0, 0, 255])
        self.drawLineList(getShapeListWithLabel(self.line_list, "Door"), [0, 0, 255])

        self.drawLineList(getShapeListWithLabel(self.line_list, "SingleConnect"), [255, 0, 0])

        self.drawLineList(getShapeListWithLabel(self.line_list, "MaybeWindow"), [0, 255, 0])
        return True

def demo_with_edit_config(config, kv_list):
    for k, v in kv_list:
        config[k] = v
    dxf_layout_detector = DXFLayoutDetector(config)
    dxf_layout_detector.render()
    return True

def demo_debug():
    config = CONFIG_COLLECTION['test1']

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

