#!/usr/bin/env python
# -*- coding: utf-8 -*-

from autocad_manage.Module.autocad_server import AutoCADServer


def demo():
    autocad_server = AutoCADServer()
    autocad_server.start()
    return True
