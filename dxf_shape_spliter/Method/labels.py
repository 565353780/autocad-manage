#!/usr/bin/env python
# -*- coding: utf-8 -*-

def getShapeListWithLabel(shape_list, label, label_value=None, unused_label_list=[]):
    shape_list_with_label = []
    for shape in shape_list:
        if not shape.isMatchLabel(label, label_value):
            continue
        if shape.isMatchAnyLabel(unused_label_list):
            continue
        shape_list_with_label.append(shape)
    return shape_list_with_label

def getShapeListWithAllLabelList(shape_list, label_list, label_value_list=None, unused_label_list=[]):
    shape_list_with_all_label_list = []
    for shape in shape_list:
        if not shape.isMatchLabelList(label_list, label_value_list):
            continue
        if shape.isMatchAnyLabel(unused_label_list):
            continue
        shape_list_with_all_label_list.append(shape)
    return shape_list_with_all_label_list

def getShapeListWithAnyLabelList(shape_list, label_list, unused_label_list=[]):
    shape_list_with_any_label_list = []
    for shape in shape_list:
        if not shape.isMatchAnyLabel(label_list):
            continue
        if shape.isMatchAnyLabel(unused_label_list):
            continue
        shape_list_with_any_label_list.append(shape)
    return shape_list_with_any_label_list

def getShapeListDictWithLabel(shape_list, label, unused_label_list=[]):
    shape_list_dict_with_label = {}
    for shape in shape_list:
        shape_label = shape.getLabel(label)
        if shape_label is None:
            continue
        if shape.isMatchAnyLabel(unused_label_list):
            continue

        if shape_label not in shape_list_dict_with_label.keys():
            shape_list_dict_with_label[shape_label] = [shape]
            continue

        shape_list_dict_with_label[shape_label].append(shape)
    return shape_list_dict_with_label

