import json, os, re
import Api.utility as util
from datetime import datetime, timedelta

def main(dist, request_data):
    all_dir = list()
    all_dist_dir = os.listdir(dist)
    imageInfo_list = list()
    imageInfo = {
        'date': '',
        'time': '',
        'address': '',
        'keywords': [],
        'wordlist': [],
        'rawtext': '',
    }
    
    date_pattern = '%Y-%m-%d'
    datetime_pattern = '%Y/%m/%d %H:%M:%S'
    reg_datetime_pattern = '^\d{4}/\d{2}/\d{2} \d{2}:\d{2}:\d{2}$'
    
    userQueryText = request_data['userQueryText'] # 欲查詢的使用者集合
    userQueryType = request_data['userQueryType'] # 欲查詢使用者的類別
    orQueryText = request_data['orQueryText'] # 欲查詢的OR字詞集合
    andQueryText = request_data['andQueryText'] # 欲查詢的AND字詞集合
    notQueryText = request_data['notQueryText'] # 欲查詢的NOT字詞集合
    
    
    if (re.search(reg_datetime_pattern, request_data['startDatetime']) == None or re.search(reg_datetime_pattern, request_data['stopDatetime']) == None):
        backdays = request_data['backdays'] # 取最近n天的資料
        all_dir = sorted(filter(lambda x: os.path.isdir(f'{dist}/{x}'), os.listdir(dist)), key=lambda x: datetime.strptime(x, '%Y-%m-%d'), reverse = True)
        backdays = backdays if len(all_dir) >= backdays else len(all_dir)
        all_dir = all_dir[:backdays]
        
        # 讀日期範圍內的json檔來篩選computer_id、time與query_text
        for directory in all_dir:
            with open(f'{dist}/{directory}/{directory}_log.json', 'r', encoding='utf-8') as f:
                pic_data = json.load(f)
                f.close()
                for pic in pic_data:
                    
                    # 判斷目標用戶
                    is_target_id = {
                        '電腦名稱': userQueryText in pic['computer_id'],
                        '員工編號': userQueryText in util.get_id(pic['computer_id']),
                        'ASEID': userQueryText in util.get_aseid(pic['computer_id']),
                        '員工姓名': userQueryText in util.get_computer_user_name(pic['computer_id']),
                        '部門代碼': userQueryText in util.get_department_id(pic['computer_id'])
                    }[userQueryType]
                    
                    #判斷AND、OR與NOT條件
                    is_target_rawtext = any([
                        len(orQueryText) == 0 and len(andQueryText) == 0 and len(notQueryText) == 0, # 無條件
                        all([
                            any([
                                any([ text in pic['rawtext'] for text in orQueryText]), # OR
                                all([ text in pic['rawtext'] for text in andQueryText]), # AND
                            ]),
                            not any([ text in pic['rawtext'] for text in notQueryText]) # NOT
                        ])
                    ])                

                    # 須 [為目標id、time與rawtext] 為真
                    if (is_target_id and is_target_rawtext):
                        temp_imageInfo = imageInfo.copy()
                        temp_imageInfo['user'] = {
                            'computer_id': pic['computer_id'],
                            'id': util.get_id(pic['computer_id']),
                            'name': util.get_computer_user_name(pic['computer_id']),
                            'ase_id': util.get_aseid(pic['computer_id']),
                            'department_id': util.get_department_id(pic['computer_id'])
                        }
                        temp_imageInfo['date'] = pic['snapshot_date']
                        temp_imageInfo['time'] = pic["snapshot_time"]
                        temp_imageInfo['address'] = pic["address"]
                        temp_imageInfo['keywords'] = list(map(lambda x: get_CloudData_fmt(x), pic["keywords"]))
                        temp_imageInfo['wordlist'] = list(map(lambda x: get_CloudData_fmt(x), pic["wordlist"]))
                        temp_imageInfo['rawtext'] = pic["rawtext"]
                        imageInfo_list.append(temp_imageInfo)
        imageInfo_list = sorted(imageInfo_list, key = lambda x: datetime.strptime(f'{x["date"]} {x["time"]}', datetime_pattern), reverse = True)
        return json.dumps({'data': {
                'start_datetime': '',
                'stop_datetime': '',
                'imageInfo': imageInfo_list
            }}, ensure_ascii = False)
    else:
        start_datetime = datetime.strptime(request_data['startDatetime'], datetime_pattern) # 取最近n天的資料
        stop_datetime = datetime.strptime(request_data['stopDatetime'], datetime_pattern) # 取最近n天的資料
        # 過濾目標時間範圍內的資料夾
        for name in all_dist_dir:
                if os.path.isdir(f'{dist}/{name}'):
                    cur_dir_date = datetime.strptime(name, date_pattern).date()
                    if cur_dir_date >= start_datetime.date() and cur_dir_date <= stop_datetime.date():
                        all_dir.append(name)
        all_dir = sorted(all_dir, key = lambda x: datetime.strptime(x, date_pattern), reverse = True)
        
        # 讀日期範圍內的json檔來篩選computer_id、time與query_text
        for directory in all_dir:
            with open(f'{dist}/{directory}/{directory}_log.json', 'r', encoding='utf-8') as f:
                pic_data = json.load(f)
                f.close()
                for pic in pic_data:
                    
                    # 判斷目標用戶
                    is_target_id = {
                        '電腦名稱': userQueryText in pic['computer_id'],
                        '員工編號': userQueryText in util.get_id(pic['computer_id']),
                        'ASEID': userQueryText in util.get_aseid(pic['computer_id']),
                        '員工姓名': userQueryText in util.get_computer_user_name(pic['computer_id']),
                        '部門代碼': userQueryText in util.get_department_id(pic['computer_id'])
                    }[userQueryType]
                    
                    # 判斷日期範圍
                    cur_pic_datetime = datetime.strptime(f'{pic["snapshot_date"]} {pic["snapshot_time"]}', datetime_pattern)
                    is_target_datetime = cur_pic_datetime >= start_datetime and cur_pic_datetime <= stop_datetime
                    
                    #判斷AND、OR與NOT條件
                    is_target_rawtext = any([
                        len(orQueryText) == 0 and len(andQueryText) == 0 and len(notQueryText) == 0, # 無條件
                        all([
                            any([
                                any([ text in pic['rawtext'] for text in orQueryText]), # OR
                                False if len(andQueryText) == 0 else all([ text in pic['rawtext'] for text in andQueryText]), # AND
                            ]),
                            not any([ text in pic['rawtext'] for text in notQueryText]) # NOT
                        ])
                    ])

                    # 須 [為目標id、time與rawtext] 為真
                    if (is_target_id and is_target_datetime and is_target_rawtext):
                        temp_imageInfo = imageInfo.copy()
                        temp_imageInfo['user'] = {
                            'computer_id': pic['computer_id'],
                            'id': util.get_id(pic['computer_id']),
                            'name': util.get_computer_user_name(pic['computer_id']),
                            'ase_id': util.get_aseid(pic['computer_id']),
                            'department_id': util.get_department_id(pic['computer_id'])
                        }
                        temp_imageInfo['date'] = pic['snapshot_date']
                        temp_imageInfo['time'] = pic["snapshot_time"]
                        temp_imageInfo['address'] = pic["address"]
                        temp_imageInfo['keywords'] = list(map(lambda x: get_CloudData_fmt(x), pic["keywords"]))
                        temp_imageInfo['wordlist'] = list(map(lambda x: get_CloudData_fmt(x), pic["wordlist"]))
                        temp_imageInfo['rawtext'] = pic["rawtext"]
                        imageInfo_list.append(temp_imageInfo)
                    
        imageInfo_list = sorted(imageInfo_list, key = lambda x: datetime.strptime(f'{x["date"]} {x["time"]}', datetime_pattern), reverse = True)
        return json.dumps({'data': {
                'start_datetime': start_datetime.strftime(datetime_pattern),
                'stop_datetime': stop_datetime.strftime(datetime_pattern),
                'imageInfo': imageInfo_list
            }}, ensure_ascii = False)
    
def get_CloudData_fmt(data_list):
    return {
        'text': data_list[0],
        'weight': data_list[1],
        'color': '',
        'tooltip': '',
    }