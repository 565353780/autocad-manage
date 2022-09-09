#!/usr/bin/env python
# -*- coding: utf-8 -*-

from autocad_manage.Config.image import PNG_PARAM, JPG_PARAM

def getImageParam(image_format):
    image_param = None
    if image_format == "png":
        image_param = PNG_PARAM
    elif image_format in ["jpg", "jpeg"]:
        image_param = JPG_PARAM
    return image_param

