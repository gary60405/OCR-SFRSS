import json, os, re
import Api.utility as util
from datetime import datetime, timedelta

def main(dist, request_data):
    userQueryType = request_data['userQueryType']
    return json.dumps({
        'data': {
            '員工編號': list(set(map(lambda x: x['id'], util.database))), 
            'ASEID': list(set(map(lambda x: x['ase_id'], util.database))), 
            '員工姓名': list(set(map(lambda x: x['name'], util.database))), 
            '電腦名稱': list(set(map(lambda x: x['computer_id'], util.database))), 
            '部門代碼': list(set(map(lambda x: x['department_id'], util.database))), 
        }[userQueryType]
    })