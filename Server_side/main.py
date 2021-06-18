# -*- coding: utf-8 -*-
import os, json, threading
from typing import Dict
from flask import Flask, request, send_from_directory
from flask_cors import CORS
from datetime import timedelta,date

from Api import Frontend_api
from AseOcr import Ocr
from waitress import serve

app = Flask(__name__)
app.config["DEBUG"] = True
app.config['DIST_FOLDER'] = 'C:/test_pic/dist'
CORS(app)

@app.route('/', methods=['POST'])
def root():
    return api.strategy_executer('save_image', request.get_json())

# host static img
@app.route('/static/<string:date_dir>/<string:user_dir>/<string:filename>', methods=['GET'])
def download_file(date_dir, user_dir, filename):
    return send_from_directory(app.config['DIST_FOLDER'], f'{date_dir}/{user_dir}/{filename}')

@app.route('/get_image_info', methods=['POST'])
def get_image_info():
    return api.strategy_executer('get_image_info', request.get_json())

@app.route('/get_keyword_user', methods=['POST'])
def get_keyword_user():
    return api.strategy_executer('get_keyword_user', request.get_json())

@app.route('/get_userdata', methods=['POST'])
def get_userdata():
    return api.strategy_executer('get_userdata', request.get_json())

@app.route('/get_all_keyword', methods=['POST'])
def get_all_keyword():
    return api.strategy_executer('get_all_keyword', request.get_json())



if __name__ == '__main__':
    api = Frontend_api(app.config['DIST_FOLDER'])
    
    api_serve_thread = threading.Thread(target = lambda: serve(app, host='127.0.0.1', port=5031, threads=6))
    api_serve_thread.start()
    
    # executor = Ocr(scan_path='C:/test_pic/dist', 
    #                 server_assets_path = 'G:/我的雲端硬碟/同步工作區/OCR-SFRSS/Server_side/assets', 
    #                 keyword_file = 'ase_keyword.txt', 
    #                 stopword_file = 'stopword.txt',
    #                 debug=True)
    # ocr_executor_thread = threading.Thread(target = lambda: executor.handler())
    # ocr_executor_thread.start()
    
    