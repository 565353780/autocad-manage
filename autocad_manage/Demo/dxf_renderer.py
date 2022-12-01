#!/usr/bin/env python
# -*- coding: utf-8 -*-

import cv2

from autocad_manage.Module.dxf_renderer import DXFRenderer


def demo():
    dxf_file_path = "/home/chli/chLi/CAD/DXF/订单图纸/40mm层板生产详图+台面图用于时光木语2.dxf"
    save_image_file_path = "/home/chli/chLi/CAD/Image/订单图纸/40mm层板生产详图+台面图用于时光木语2.png"
    compare_with_all_shape = True

    dxf_renderer = DXFRenderer(dxf_file_path)
    dxf_renderer.outputInfo()
    dxf_renderer.saveImage(save_image_file_path, compare_with_all_shape)
    dxf_renderer.render()
    cv2.waitKey(10000)
    return True
