import cv2
import numpy as np

# 圖片hash(雜湊)編碼
def pHash(img):
    
    # 缩放32*32
    img = cv2.resize(img, (32, 32))
    # 轉換為灰度圖
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    # 將灰度圖轉為浮點型，再進行dct變換
    dct = cv2.dct(np.float32(gray))
    dct_roi = dct[0:8, 0:8]
    
    hash = []
    avreage = np.mean(dct_roi)
    for i in range(dct_roi.shape[0]):
        for j in range(dct_roi.shape[1]):
            if dct_roi[i, j] > avreage:
                hash.append(1)
            else:
                hash.append(0)
    return hash

# hash值比較
def cmpHash(hash1, hash2):
    # 每張圖經過hash(雜湊)演算，會有自己所對應的二進位編碼，透過計算漢明距離，即兩個64位的hash值有多少是不一樣的，不同的位數越小，圖片越相似。
    n = 0
    # hash長度不同則返回-1代表傳參出錯
    if len(hash1) != len(hash2):
        return -1
    # 遍歷判斷
    for i in range(len(hash1)):
        # 不相等則n計數+1，n最終為相似度
        if hash1[i] != hash2[i]:
            n = n + 1
    return n

def IMG_comparing(img1, img2):
    hash1 = pHash(img1)
    hash2 = pHash(img2)
    distance = cmpHash(hash1, hash2)
    toatal_distance = 64
    return round(1 - distance / toatal_distance, 2)
    
if __name__ == "__main__":
    pic_1 = cv2.imread('compare_1.png')
    pic_2 = cv2.imread('test.png')
    IMG_comparing(pic_1, pic_2)
    print(IMG_comparing(pic_1, pic_2))