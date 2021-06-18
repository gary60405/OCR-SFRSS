import os, ctypes, platform
from random import shuffle, randint

database = [{'computer_id': 'ASE_5', 'name': '吳小語', 'id': '95084295', 'ase_id': 'K21615', 'department_id': 'DEP002'}, {'computer_id': 'ASE_4', 'name': '鄭和尚', 'id': '95758576', 'ase_id': 'K31211', 'department_id': 'DEP005'}, {'computer_id': 'ASE_7', 'name': '王和強', 'id': '95887654', 'ase_id': 'K25064', 'department_id': 'DEP001'}, {'computer_id': 'ASE_2', 'name': '高長語', 'id': '97106820', 'ase_id': 'K26331', 'department_id': 'DEP001'}, {'computer_id': 'NCKU', 'name': '王小尚', 'id': '95162635', 'ase_id': 'K18719', 'department_id': 'DEP003'}, {'computer_id': 'ASE_3', 'name': '李上偉', 'id': '96840598', 'ase_id': 'K29504', 'department_id': 'DEP005'}, {'computer_id': 'ASE_1', 'name': '鄭上線', 'id': '96542832', 'ase_id': 'K23950', 'department_id': 'DEP002'}, {'computer_id': 'ASE_6', 'name': '許和語', 'id': '95447322', 'ase_id': 'K19568', 'department_id': 'DEP004'}]


def get_department_id(computer_id):
    return list(filter(lambda x: x['computer_id'] == computer_id, database))[0]['department_id']
    # return {
    #     '1': 'DEP001',
    #     '2': 'DEP002',
    #     '3': 'DEP003',
    #     '4': 'DEP004',
    #     '5': 'DEP005',
    #     }[str(randint(1, 5))]

def get_aseid(computer_id):
    return list(filter(lambda x: x['computer_id'] == computer_id, database))[0]['ase_id']
    # return f'K{randint(15000, 35000)}'

def get_id(computer_id):
    return list(filter(lambda x: x['computer_id'] == computer_id, database))[0]['id']
    # return str(randint(95000000, 98000000))

def get_computer_user_name(computer_id):
    return list(filter(lambda x: x['computer_id'] == computer_id, database))[0]['name']
    # first = ['王', '李', '陳', '林', '吳', '鄭', '許', '周', '顏', '高']
    # middle = ['小', '大', '長','和', '上']
    # last = ['明', '強', '婷', '均', '偉', '語', '琪', '線', '尚']
    # shuffle(first)
    # shuffle(middle)
    # shuffle(last)
    # return f'{first[0]}{middle[0]}{last[0]}'

def is_disk_free(folder, threshold): # 硬碟空間防呆機制
    '''
    :param folder: int 預計算的硬碟位置ex：'C:\'。
    :param threshold: int 最低容量限度(單位GB)。
    '''
    if platform.system() == 'Windows':
        free_bytes = ctypes.c_ulonglong(0)
        ctypes.windll.kernel32.GetDiskFreeSpaceExW(ctypes.c_wchar_p(folder), None, None, ctypes.pointer(free_bytes))
        return free_bytes.value/1024/1024/1024 >= threshold
    else:
        st = os.statvfs(folder)
        return st.f_bavail * st.f_frsize/1024/1024 >= threshold

# 產生DB的假資料
# if __name__ == '__main__':
#     opt_list = []
#     for user in ['ASE_5', 'ASE_4', 'ASE_7', 'ASE_2', 'NCKU', 'ASE_3', 'ASE_1', 'ASE_6']:
#         output = {}
#         output['computer_id'] = user
#         output['name'] = get_computer_user_name(user)
#         output['id'] = get_id(user)
#         output['ase_id'] = get_aseid(user)
#         output['department_id'] = get_department_id(user)
#         opt_list.append(output)
#     print(opt_list)