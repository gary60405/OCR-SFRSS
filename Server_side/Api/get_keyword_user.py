import json, os, re
import Api.utility as util
from datetime import datetime

def main(dist, request_data):
    all_dir = list()
    all_dist_dir = os.listdir(dist)
    keyword_user_list = list()
    
    date_pattern = '%Y-%m-%d'
    datetime_pattern = '%Y/%m/%d %H:%M:%S'
    reg_datetime_pattern = '^\d{4}/\d{2}/\d{2} \d{2}:\d{2}:\d{2}$'
    
    
    rawtextQueryText = request_data['rawtextQueryText'] # 欲查詢的字詞
    
    # 如果時間範圍設定不完整，則預設最近n天內的資料
    if (re.search(reg_datetime_pattern, request_data['startDatetime']) == None or re.search(reg_datetime_pattern, request_data['stopDatetime']) == None):
        backdays = request_data['backdays'] # 取最近n天的資料
        all_dir = sorted(filter(lambda x: os.path.isdir(f'{dist}/{x}'), os.listdir(dist)), key=lambda x: datetime.strptime(x, '%Y-%m-%d'), reverse = True)
        backdays = backdays if len(all_dir) >= backdays else len(all_dir)
        all_dir = all_dir[:backdays]
        
        # 讀日期範圍內的json檔來篩選query_text
        for directory in all_dir:
            with open(f'{dist}/{directory}/{directory}_log.json', 'r', encoding='utf-8') as f:
                pic_data = json.load(f)
                f.close()
                for pic in pic_data:
                    cur_pic_datetime = datetime.strptime(f'{pic["snapshot_date"]} {pic["snapshot_time"]}', datetime_pattern)
                    
                    #若查詢集為空則一律為True，否則視查詢字是否存在rawtext而定
                    is_target_rawtext = True if rawtextQueryText == '' else ( rawtextQueryText in pic['rawtext'] )
                    is_target_keyword = True if rawtextQueryText == '' else ( any([ keyword[0] == rawtextQueryText for keyword in pic['keywords'] ]) )
                    
                    # 須 [目標rawtext、datetime] 為真
                    if is_target_rawtext and is_target_keyword:
                        imageInfo = {
                            'computer_id': pic['computer_id'],
                            'id': util.get_id(pic['computer_id']),
                            'name': util.get_computer_user_name(pic['computer_id']),
                            'ase_id': util.get_aseid(pic['computer_id']),
                            'department_id': util.get_department_id(pic['computer_id']),
                            'datetime': f'{pic["snapshot_date"]} {pic["snapshot_time"]}',
                            'address': pic['address']
                        }
                        keyword_user_list.append(imageInfo)

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
        
        # 讀日期範圍內的json檔來篩選query_text
        for directory in all_dir:
            with open(f'{dist}/{directory}/{directory}_log.json', 'r', encoding='utf-8') as f:
                pic_data = json.load(f)
                f.close()
                for pic in pic_data:
                    cur_pic_datetime = datetime.strptime(f'{pic["snapshot_date"]} {pic["snapshot_time"]}', datetime_pattern)
                    is_target_datetime = cur_pic_datetime >= start_datetime and cur_pic_datetime <= stop_datetime # 是否落在目標時間
                    
                    #若查詢集為空則一律為True，否則視查詢字是否存在rawtext而定
                    is_target_rawtext = True if rawtextQueryText == '' else ( rawtextQueryText in pic['rawtext'] )
                    is_target_keyword = True if rawtextQueryText == '' else ( any([ keyword[0] == rawtextQueryText for keyword in pic['keywords'] ]) )
                    
                    # 須 [目標rawtext、datetime] 為真
                    if is_target_rawtext and is_target_datetime and is_target_keyword:
                        imageInfo = {
                            'computer_id': pic['computer_id'],
                            'id': util.get_id(pic['computer_id']),
                            'name': util.get_computer_user_name(pic['computer_id']),
                            'ase_id': util.get_aseid(pic['computer_id']),
                            'department_id': util.get_department_id(pic['computer_id']),
                            'datetime': f'{pic["snapshot_date"]} {pic["snapshot_time"]}',
                            'address': pic['address']
                        }
                        keyword_user_list.append(imageInfo)
                    
    keyword_user_list = sorted(keyword_user_list, key = lambda x: datetime.strptime(x['datetime'], datetime_pattern), reverse=True)
    return json.dumps({'data': keyword_user_list}, ensure_ascii = False)