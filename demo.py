#!/usr/bin/env python
# -*- coding: utf-8 -*-

from autocad_manage.Demo.dxf_loader import \
    demo as dxf_load_demo, \
    demo_folder as dxf_load_folder_demo

from autocad_manage.Demo.dxf_renderer import \
    demo as dxf_render_demo

from autocad_manage.Demo.dxf_layout_detector import \
    demo as layout_detect_demo, \
    demo_trans as layout_trans_demo, \
    demo_trans_folder as layout_trans_folder_demo

if __name__ == "__main__":
    dxf_load_demo()
    #  dxf_load_folder_demo()

    #  dxf_render_demo()

    #  layout_detect_demo()
    #  layout_trans_demo()
    #  layout_trans_folder_demo()
