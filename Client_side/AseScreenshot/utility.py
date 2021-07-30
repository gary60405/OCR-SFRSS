import zlib, base64, re, os
from io import BytesIO
from PIL import Image
from datetime import datetime
    
def image_to_base64(img):
    output_buffer = BytesIO()
    img.save(output_buffer, format='png')
    byte_data = output_buffer.getvalue()
    base64_str = base64.b64encode(byte_data)
    cmp_str = zlib.compress(base64_str)
    return cmp_str

def base64_to_image(cmp_str):
    bytes_cmp_str = bytes(re.match(r"^b'(.*?)'$", cmp_str).group(1), encoding='utf-8')
    scape_bytes_cmp_str = bytes_cmp_str.decode('unicode-escape').encode('ISO-8859-1')
    base64_str = zlib.decompress(scape_bytes_cmp_str) # 解壓縮base64_str
    byte_data = base64.b64decode(base64_str)
    image_data = BytesIO(byte_data)
    return Image.open(image_data)

def text_to_base64(text):
    return zlib.compress(base64.b64encode(bytes(text, 'utf-8')))

def base64_to_text(cmp_str):
    bytes_cmp_str = bytes(re.match(r"^b'(.*?)'$", cmp_str).group(1), encoding='utf-8')
    scape_bytes_cmp_str = bytes_cmp_str.decode('unicode-escape').encode('ISO-8859-1')
    base64_str = zlib.decompress(scape_bytes_cmp_str) # 解壓縮base64_str
    return base64.b64decode(base64_str).decode("utf-8")

# def filename_to_time(filename):
#     items = filename.split(' ')
#     return mktime(strptime(f'{items[1]}{items[2].replace(".png", "")}', '%Y-%m-%d%H.%M.%S'))

def get_last_pic(secret_file, rowsplitor, colsplitor):
    if os.path.isfile(secret_file):
        return base64_to_image(open(secret_file, 'r').read().split(rowsplitor)[-1].split(colsplitor)[1])
    else:
        return ''

def get_first_data(secret_file, rowsplitor, colsplitor, max_buffer_file  = 3):
    if os.path.isfile(secret_file):
        file_data = open(secret_file, 'r').read()
        data = file_data.split(rowsplitor)[0].split(colsplitor)
        is_reach_max =  file_data.count(rowsplitor) + 1 >= max_buffer_file
        return data[0], data[1], is_reach_max
    else:
        return '', '', ''
    
def save_to_secret(file_path, image, type, rowsplitor, colsplitor):
    with open(file_path, type, encoding = 'utf-8') as f:
        time_stamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        f.write(f'{rowsplitor if type == "a+" else ""}{text_to_base64(time_stamp)}{colsplitor}{image_to_base64(image)}')
        f.close()