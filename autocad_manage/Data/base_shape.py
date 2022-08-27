#!/usr/bin/env python
# -*- coding: utf-8 -*-

from autocad_manage.Data.label import Label

class BaseShape(Label):
    def __init__(self):
        super(BaseShape, self).__init__()
        self.type = "BASESHAPE"
        self.attribs_dict = {}
        return

    def setAttribsDict(self, attribs_dict):
        self.attribs_dict = attribs_dict
        return True

    def getJson(self):
        json_dict = {}
        for key, item in self.attribs_dict.items():
            json_dict[key] = str(item)
        return json_dict

