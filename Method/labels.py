#!/usr/bin/env python
# -*- coding: utf-8 -*-

def getShapeListWithLabel(shape_list, label, label_value=True):
    shape_list_with_label = []
    for shape in shape_list:
        shape_label = shape.getLabel(label)
        if shape_label is None:
            continue
        if shape_label != label_value:
            continue
        shape_list_with_label.append(shape)
    return shape_list_with_label

def getShapeListDictWithLabel(shape_list, label):
    shape_list_dict_with_label = {}
    for shape in shape_list:
        shape_label = shape.getLabel(label)
        if shape_label is None:
            continue

        if shape_label not in shape_list_dict_with_label.keys():
            shape_list_dict_with_label[shape_label] = [shape]
            continue

        shape_list_dict_with_label[shape_label].append(shape)
    return shape_list_dict_with_label

