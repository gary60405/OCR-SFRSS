# -*- coding: utf-8 -*-
import numpy as np
import AseOcr.preprocessing as preproc
import os, re, jieba, json, collections, time, portalocker
from PIL import Image
from pytesseract import image_to_string
from pycorrector import set_custom_confusion_dict, set_custom_word_freq, traditional2simplified, simplified2traditional, correct


class Ocr():
    def __init__(self, scan_path, server_assets_path, keyword_file, stopword_file, debug = False):
        self.scan_path = scan_path
        self.server_assets_path = server_assets_path
        self.keyword_file = keyword_file
        self.stopword_file = stopword_file
        
        self.stop_words = list()
        self.keywords = list()
        self.cc_t2s = None
        self.cc_s2t = None
        self.debug = debug

    def initialize(self):
        jieba.set_dictionary(f'{self.server_assets_path}/dict.big.txt')
        jieba.load_userdict(f'{self.server_assets_path}/ase_jieba_dict.txt')
        set_custom_confusion_dict(path = f'{self.server_assets_path}/my_custom_confusion.txt')
        set_custom_word_freq(path = f'{self.server_assets_path}/my_custom_word_freq.txt')
        
        with open(f'{self.server_assets_path}/{self.stopword_file}', 'r', encoding='utf-8') as f:
            self.stop_words = f.read().split('\n')
            f.close()
        
        with open(f'{self.server_assets_path}/{self.keyword_file}', 'r', encoding='utf-8') as f:
            self.keywords = [keyword for keyword in map(lambda x: x.replace('\n', ''), f.readlines())]
            f.close()

    def image_preprocessing(self, filename):
        transformer = preproc.IMG_preprocessing(filename)
        if transformer.is_blackbased_image(): 
            transformer.to_reverse_color() # 若為黑底則反轉圖片顏色
        transformer.to_denoising()
        transformer.to_add_contrast(alpha = 1)
        transformer.to_filtering()
        transformer.to_resize()
        opencv_img = transformer.get_img()
        return Image.fromarray(opencv_img) # cv2 to PIL Image

    def get_keywordlist(self, word_list):
        return list(filter(lambda x: x[0] in self.keywords, word_list))
    
    def get_wordlist(self, tra_text):
        cut_list = jieba.cut(tra_text)
        filterd_word_lengh = list(filter(lambda x: len(x) > 1, cut_list)) # 素過濾斷詞後只有一個字的元
        filterd_number = list(filter(lambda x: not x.isdigit(), filterd_word_lengh)) # 過濾純數字的字
        filterd_word = list(filter(lambda x: x not in self.stop_words, filterd_number)) # 過濾停用詞
        word_dict = collections.Counter(filterd_word) # 統計所有斷詞的出現次數
        return list(word_dict.items())
    
    def save_to_json(self, output_obj):
        final_output = []
        json_path = f'{self.scan_path}/{output_obj["snapshot_date"]}/{output_obj["snapshot_date"]}_log.json'
        
        output_obj["snapshot_date"] = output_obj["snapshot_date"].replace('-', '/')
        output_obj["snapshot_time"] = output_obj["snapshot_time"].replace('-', ':')
        
        is_first = not os.path.exists(json_path)
        if not is_first:
            with open(json_path, 'r', encoding='utf-8') as f:
                final_output = json.load(f)
                f.close()
        with open(json_path, 'w', encoding='utf-8') as f:
            final_output.append(output_obj)
            f.write(json.dumps(final_output, ensure_ascii=False))
            f.close()
        if self.debug:
            print(f"[JSON appended] {output_obj['address']}")
        
    def handler(self):
        self.initialize() # 初始化
        while True:
            retry_times = 100 # 搶lock失敗的重試次數
            for i in range(retry_times):
                try:
                    fh = open(f'{self.scan_path}/share_temp_file.log', 'a+', encoding='utf-8') # 開啟共享文件load檔名出來
                    portalocker.Lock(fh, timeout = 60) # lock住檔案權限
                    fh.seek(0)
                    filenames = list(filter(lambda x: x != '', fh.read().split('\n')))
                    fh.truncate(0) # load完就清空
                    fh.flush() # 歸還lock
                    os.fsync(fh.fileno())
                    with open(f'{self.scan_path}/temp_file_queue.log', 'a+', encoding='utf-8') as f: # 開啟僅有本檔案所維護的filename queue
                        if len(filenames) != 0: # 「共享文件」有filename才寫入
                            f.write('\n'.join(filenames) + '\n') # 新增讀入的filenames
                        f.seek(0)
                        filenames = list(filter(lambda x: x != '', f.read().split('\n')))
                        if len(filenames) != 0: # 「filename queue」有filename才往下做
                            tra_text = ''
                            word_list, keywords_list = list(), list()
                            filename = filenames[0] # 一次只讀第一個檔案
                            pattern = re.match('^(.+)_(\d{4}-\d{2}-\d{2})_(\d{2}-\d{2}-\d{2}).png$', filename)
                            username = pattern.group(1)
                            snapshot_date = pattern.group(2)
                            snapshot_time = pattern.group(3)
                            try:
                                pil_image = self.image_preprocessing(f'{self.scan_path}/{snapshot_date}/{username}/{filename}')
                                rcn_result = image_to_string(pil_image, lang='ase_chi_tra_3', config = r'--oem 3 --psm 6') # OCR辨識
                                sim_text = traditional2simplified(rcn_result.replace(' ', '').replace('\n', '')) # 繁轉簡
                                corrected_sent, _ = correct(sim_text) # 糾正錯字
                                tra_text = simplified2traditional(corrected_sent) # 簡轉繁
                                word_list = self.get_wordlist(tra_text)
                                keywords_list = self.get_keywordlist(word_list)
                            except Exception as e:
                                print(f'[Recognition Fail] Message：{e}')
                                continue
                            self.save_to_json({
                                'computer_id': username,
                                'snapshot_date': snapshot_date,
                                'snapshot_time': snapshot_time,
                                'address': f'{snapshot_date}/{username}/{filename}',
                                'keywords': keywords_list,
                                'wordlist': word_list,
                                'rawtext': tra_text
                                })
                            f.truncate(0) # 確認儲存成功才清空
                            f.write('\n'.join(filenames[1:]) + '\n') # 濾除第一個檔案(已完成)並重新寫入檔案
                        f.close()
                except Exception as e:
                    print(f'[Get Lock Fail] To read temp_file.log (Message：{e})')
                    time.sleep(1)
                    continue
        

if __name__ == "__main__":
    executor = Ocr(scan_path='C:/test_pic/dist', 
                    server_assets_path = 'G:/我的雲端硬碟/同步工作區/OCR-SFRSS/Server_side/assets', 
                    keyword_file = 'ase_keyword.txt', 
                    stopword_file = 'stopword.txt',
                    debug=True)
    executor.handler()