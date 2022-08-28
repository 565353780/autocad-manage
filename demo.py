#!/usr/bin/env python
# -*- coding: utf-8 -*-

from autocad_manage.Module.dwg_loader import \
    demo as dwg_load_demo, \
    demo_folder as dwg_load_folder_demo
from autocad_manage.Module.dxf_loader import \
    demo as dxf_load_demo, \
    demo_folder as dxf_load_folder_demo
from autocad_manage.Module.dxf_layout_detector import \
    demo as layout_detect_demo, \
    demo_debug as layout_detect_debug_demo

if __name__ == "__main__":
    #  dwg_load_demo()
    dwg_load_folder_demo()
    #  dxf_load_demo()
    #  dxf_load_folder_demo()
    #  layout_detect_demo()
    #  layout_detect_debug_demo()

