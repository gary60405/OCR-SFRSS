import os, time, portalocker
import AseOcr.utility as util

def main(dist, request_data):
    try:
        min_disk_space = 1 # 單位：GB
        if True: # is_disk_free('C:/', min_disk_space): deployment再打開
            user = request_data['computer_id']
            timestamp = util.base64_to_text(request_data['timestamp']) \
                            .replace(":", "-") \
                            .replace(" ", "_")
            img = util.base64_to_image(request_data['data'])
            
            if not os.path.exists(f'{dist}/{timestamp.split("_")[0]}/{user}'):
                os.makedirs(f'{dist}/{timestamp.split("_")[0]}/{user}')
            img.save(f'{dist}/{timestamp.split("_")[0]}/{user}/{user}_{timestamp}.png')
            
            retry_times = 100 # 搶lock失敗的重試次數        
            for _ in range(retry_times):
                try:
                    fh = open(f'{dist}/share_temp_file.log', 'a+', encoding='utf-8')
                    portalocker.Lock(fh, timeout = 60)
                    fh.write(f'{user}_{timestamp}.png\n')
                    fh.flush()
                    os.fsync(fh.fileno())
                    break
                except Exception as e:
                    print(f'[Get Lock Fail] To wirte {user}_{timestamp}.png in temp_file.log (Message：{e})')
                    time.sleep(1)
                    continue
            return f'SAVE {dist}/{timestamp.split("_")[0]}/{user}/{user}_{timestamp}.png'
        else:
            print(f'[圖檔無法儲存] 硬碟空間已少於{min_disk_space}GB!!')
            return f'[圖檔無法儲存] 硬碟空間已少於{min_disk_space}GB!!'
    except BaseException as e:
        print(e)
        return e