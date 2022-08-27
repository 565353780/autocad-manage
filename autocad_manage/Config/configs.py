#!/usr/bin/env python
# -*- coding: utf-8 -*-

from copy import deepcopy

from autocad_manage.Config.base_config import BASE_CONFIG
from autocad_manage.Config.dxf_paths import DXF_DICT, VALID_KEY_LIST

RENDER_ALL = deepcopy(BASE_CONFIG)
RENDER_ALL['dxf_file_path'] = DXF_DICT[VALID_KEY_LIST[0]]
RENDER_ALL['window_name'] = 'Render all'

LAYOUT_TEST1 = deepcopy(BASE_CONFIG)
LAYOUT_TEST1['dxf_file_path'] = DXF_DICT['test1']
LAYOUT_TEST1['window_name'] = 'Layout test1'

LAYOUT_3 = deepcopy(BASE_CONFIG)
LAYOUT_3['dxf_file_path'] = DXF_DICT['3']
LAYOUT_3['window_name'] = 'Layout 3'

LAYOUT_4 = deepcopy(BASE_CONFIG)
LAYOUT_4['dxf_file_path'] = DXF_DICT['4']
LAYOUT_4['window_name'] = 'Layout 4'

LAYOUT_5 = deepcopy(BASE_CONFIG)
LAYOUT_5['dxf_file_path'] = DXF_DICT['5']
LAYOUT_5['window_name'] = 'Layout 5'

LAYOUT_6 = deepcopy(BASE_CONFIG)
LAYOUT_6['dxf_file_path'] = DXF_DICT['6']
LAYOUT_6['window_name'] = 'Layout 6'

LAYOUT_9 = deepcopy(BASE_CONFIG)
LAYOUT_9['dxf_file_path'] = DXF_DICT['9']
LAYOUT_9['window_name'] = 'Layout 9'

LAYOUT_10 = deepcopy(BASE_CONFIG)
LAYOUT_10['dxf_file_path'] = DXF_DICT['10']
LAYOUT_10['window_name'] = 'Layout 10'

CONFIG_COLLECTION = {
    'render_all': RENDER_ALL,
    'test1': LAYOUT_TEST1,
    '3': LAYOUT_3,
    '4': LAYOUT_4,
    '5': LAYOUT_5,
    '6': LAYOUT_6,
    '9': LAYOUT_9,
    '10': LAYOUT_10,
}

