#!/usr/bin/env python
# -*- coding: utf-8 -*-

import win32com.client
import comtypes.client

try:
        acad = comtypes.client.GetActiveObject("AutoCAD.Application")
except:
        acad = comtypes.client.CreateObject("AutoCAD.Application")

acad.Visible = True
doc = acad.Documents.Open("C:\\Users\\Administrator\\Desktop\\tulesheng.dwg")

class DWGLoader(object):
    def __init__(self):
        return

def demo():
    dwg_loader = DWGLoader()
    return True

