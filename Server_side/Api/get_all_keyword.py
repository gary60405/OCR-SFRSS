import os, json, re
import Api.utility as util
from datetime import datetime

def main(dist, request_data):
    keywords = {}
    all_dir = list()
    all_dist_dir = os.listdir(dist)
    
    date_pattern = '%Y-%m-%d'
    datetime_pattern = '%Y/%m/%d %H:%M:%S'
    reg_datetime_pattern = '^\d{4}/\d{2}/\d{2} \d{2}:\d{2}:\d{2}$'
    

    # 如果時間範圍設定不完整，則預設最近n天內的資料
    if (re.search(reg_datetime_pattern, request_data['startDatetime']) == None or re.search(reg_datetime_pattern, request_data['stopDatetime']) == None):
        backdays = request_data['backdays'] # 取最近n天的資料
        all_dir = sorted(filter(lambda x: os.path.isdir(f'{dist}/{x}'), os.listdir(dist)), key=lambda x: datetime.strptime(x, '%Y-%m-%d'), reverse = True)
        backdays = backdays if len(all_dir) >= backdays else len(all_dir)
        all_dir = all_dir[:backdays]
        # 讀日期範圍內的json檔來統計關鍵字  
        for directory in all_dir:
            with open(f'{dist}/{directory}/{directory}_log.json', 'r', encoding='utf-8') as f:
                pic_data = json.load(f)
                for pic in pic_data:
                    for key, cnt in pic['keywords']:
                        
                        if keywords.get(key) != None:
                            keywords[key] += int(cnt)
                        else:
                            keywords[key] = int(cnt)
    else:
        # 取時間範圍內的資料
        start_datetime = datetime.strptime(request_data['startDatetime'], datetime_pattern) 
        stop_datetime = datetime.strptime(request_data['stopDatetime'], datetime_pattern)
        for name in all_dist_dir:
                if os.path.isdir(f'{dist}/{name}'):
                    cur_dir_date = datetime.strptime(name, date_pattern).date()
                    if cur_dir_date >= start_datetime.date() and cur_dir_date <= stop_datetime.date():
                        all_dir.append(name)
        all_dir = sorted(all_dir, key = lambda x: datetime.strptime(x, date_pattern), reverse = True)
    
        # 讀日期範圍內的json檔來統計關鍵字  
        for directory in all_dir:
            with open(f'{dist}/{directory}/{directory}_log.json', 'r', encoding='utf-8') as f:
                pic_data = json.load(f)
                f.close()
                for pic in pic_data:
                    cur_pic_datetime = datetime.strptime(f'{pic["snapshot_date"]} {pic["snapshot_time"]}', datetime_pattern)
                    is_target_datetime = cur_pic_datetime >= start_datetime and cur_pic_datetime <= stop_datetime # 是否落在目標時間
                    
                    if is_target_datetime:
                        for key, cnt in pic['keywords']:
                            if keywords.get(key) != None:
                                keywords[key] += int(cnt)
                            else:   
                                keywords[key] = int(cnt)
            
    return json.dumps({'data': [ 
                get_CloudData_fmt(data)
                for data in keywords.items()
            ]}, ensure_ascii=False)
    
def get_CloudData_fmt(data_list):
    return {
        'text': data_list[0],
        'weight': data_list[1],
        'color': '',
        'tooltip': '',
    }