#!/usr/bin/env python
# -*- coding: utf-8 -*-

from autocad_manage.Module.dxf_loader import demo as load_demo
from autocad_manage.Module.dxf_layout_detector import \
    demo as layout_detect_demo, \
    demo_debug as layout_detect_debug_demo

if __name__ == "__main__":
    load_demo()
    #  layout_detect_demo()
    #  layout_detect_debug_demo()

