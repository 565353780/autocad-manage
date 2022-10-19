#!/usr/bin/env python
# -*- coding: utf-8 -*-

import cv2

from autocad_manage.Module.dxf_layout_detector import DXFLayoutDetector


def demo():
    dxf_file_path = "/home/chli/chLi/CAD/DXF/户型识别文件/1.dxf"
    save_json_file_path = "/home/chli/chLi/CAD/JSON/户型识别文件/1.json"
    save_image_file_path = "/home/chli/chLi/CAD/Image/户型识别文件/1.png"
    compare_with_all_shape = True

    dxf_layout_detector = DXFLayoutDetector(dxf_file_path)
    dxf_layout_detector.outputInfo()
    dxf_layout_detector.saveImage(save_image_file_path, compare_with_all_shape)
    dxf_layout_detector.render()
    cv2.waitKey(0)
    dxf_layout_detector.saveJson(save_json_file_path)
    return True


def demo_trans():
    dxf_file_path = "/home/chli/chLi/CAD/DXF/户型识别文件/1.dxf"
    save_json_file_path = "/home/chli/chLi/CAD/JSON/户型识别文件/1.json"
    save_image_file_path = "/home/chli/chLi/CAD/Image/户型识别文件/1.png"
    compare_with_all_shape = True

    dxf_layout_detector = DXFLayoutDetector()
    dxf_layout_detector.transDxfToJsonWithLayout(dxf_file_path,
                                                 save_json_file_path,
                                                 save_image_file_path,
                                                 compare_with_all_shape)
    return True


def demo_trans_folder():
    dxf_folder_path = "/home/chli/chLi/CAD/DXF/House_1/"
    save_json_folder_path = "/home/chli/chLi/CAD/JSON/House_1/"
    save_image_folder_path = "/home/chli/chLi/CAD/Image/House_1/"
    compare_with_all_shape = True
    print_progress = True

    dxf_layout_detector = DXFLayoutDetector()
    dxf_layout_detector.transDxfFolderToJsonWithLayout(dxf_folder_path,
                                                       save_json_folder_path,
                                                       save_image_folder_path,
                                                       compare_with_all_shape,
                                                       print_progress)
    return True
