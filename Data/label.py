#!/usr/bin/env python
# -*- coding: utf-8 -*-

class Label(object):
    def __init__(self):
        self.label_dict = {}
        return

    def setLabel(self, key, value=True):
        self.label_dict[key] = value
        return True

    def getLabel(self, key):
        value = self.label_dict.get(key)
        return value

    def getLabelStr(self):
        label_str = ""
        for key in self.label_dict:
            label_str += key
            label_str += str(self.label_dict[key])
            label_str += "_"

        if label_str == "":
            return "Unknown"

        if label_str[-1] == "_":
            label_str = label_str[:-1]
        return label_str

