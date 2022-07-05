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
            value = self.label_dict[key]
            if value is not True:
                label_str += str(self.label_dict[key])
            label_str += "_"

        if label_str == "":
            return "Unknown"

        if label_str[-1] == "_":
            label_str = label_str[:-1]
        return label_str

    def isMatchLabel(self, label, label_value=None):
        current_label_value = self.getLabel(label)
        if current_label_value is None:
            return False

        if label_value is None:
            return True

        if label_value is True:
            if current_label_value is True:
                return True
            return False

        if current_label_value == label_value:
            return True
        return False

    def isMatchLabelList(self, label_list, label_value_list=None):
        if label_value_list is None:
            label_value_list = [None for _ in label_list]

        for label, label_value in zip(label_list, label_value_list):
            if not self.isMatchLabel(label, label_value):
                return False
        return True

    def isMatchAnyLabel(self, label_list):
        for label in label_list:
            if self.isMatchLabel(label):
                return True
        return False

    def removeLabel(self, label, not_exist_ok=True):
        if not self.isMatchLabel(label):
            if not_exist_ok:
                return True
            print("[ERROR][Label::removeLabel]")
            print("\t this label [" + label + "] not exist!")
            return False

        _ = self.label_dict.pop(label)
        return True

