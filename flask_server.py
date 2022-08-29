#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import json
from flask import Flask, request

import sys
sys.path.append("../method-manage/")

from method_manage.Config.path import TMP_SAVE_FOLDER_PATH

from method_manage.Method.signal import sendDataIn, getDataOut

def demo():
    port = 9366

    app = Flask(__name__)

    os.makedirs(TMP_SAVE_FOLDER_PATH, exist_ok=True)

    @app.route('/')
    def index():
        return "Hello"

    @app.route('/transDwgToDxf', methods=['POST'])
    def transDwgToDxf():
        data = request.get_data()
        sendDataIn('transDwgToDxf', data)
        result_data = getDataOut('transDwgToDxf')
        return json.dumps(result_data, ensure_ascii=False)

    @app.route('/transDxfToJson', methods=['POST'])
    def transDxfToJson():
        data = request.get_data()
        sendDataIn('transDxfToJson', data)
        result_data = getDataOut('transDxfToJson')
        return json.dumps(result_data, ensure_ascii=False)

    @app.route('/transDwgToJson', methods=['POST'])
    def transDwgToJson():
        data = request.get_data()
        sendDataIn('transDwgToJson', data)
        result_data = getDataOut('transDwgToJson')
        return json.dumps(result_data, ensure_ascii=False)

    @app.route('/stop', methods=['POST'])
    def stop():
        sendDataIn('stop', b'1')
        result_data = getDataOut('stop')
        return json.dumps(result_data, ensure_ascii=False)

    app.run('0.0.0.0', port)
    return True

if __name__ == "__main__":
    demo()

