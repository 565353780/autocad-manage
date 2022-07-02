#!/usr/bin/env python
# -*- coding: utf-8 -*-

from Config.dxf_paths import DXF_DICT, VALID_KEY_LIST

RENDER_ALL = {
    'dxf_file_path': DXF_DICT[VALID_KEY_LIST[0]],
    'debug': True,
    'max_dist_error': 0.1,
    'image_width': 1600 * 1.2,
    'image_height': 900 * 1.2,
    'free_width': 50,
    'is_reverse_y': True,
    'window_name': 'Render all',
}

