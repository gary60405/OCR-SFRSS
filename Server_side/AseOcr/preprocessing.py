import sys
import cv2
import numpy as np
import matplotlib.pyplot as plt

class IMG_preprocessing():
  
  def __init__(self, path):
        self.input_img = cv2.imread(path)
        self.output_img = cv2.imread(path)

  def to_thresholding(self, threshold = 160, is_inverse = False, is_adative = False):
    '''
    :param is_inverse: bool 若為True則將大於threshold的值設為0(黑)，其餘設為最大灰階值，若設為False則反之。
    :param is_adative: bool 若為True則Threshold由opencv動態計算，False則由呼叫端自訂。
    詳細可參考本篇：https://shengyu7697.github.io/blog/2020/03/14/Python-OpenCV-threshold/
    '''
    self.to_grayscale()
    if is_adative:
      if is_inverse:
        _, self.output_img = cv2.threshold(self.output_img, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
      else:
        _, self.output_img = cv2.threshold(self.output_img, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    else:
      if is_inverse:
        _, self.output_img = cv2.threshold(self.output_img, threshold, 255, cv2.THRESH_BINARY_INV)
      else:
        _, self.output_img = cv2.threshold(self.output_img, threshold, 255, cv2.THRESH_BINARY)
    
  def to_grayscale(self): # 圖片灰階
    if len(self.output_img.shape) == 3 and self.output_img.shape[2] == 3:
      self.output_img = cv2.cvtColor(self.output_img, cv2.COLOR_BGR2GRAY)
      
  def to_rotate(self, image, angle): # 圖片旋轉
    #修正校正角度
    angle = angle if angle >= -80 else 90 + angle
    
    #獲取寬高
    (h, w) = image.shape[:2]
    (cX, cY) = (w // 2, h // 2)

    # 提取旋轉矩陣 sin cos 
    M = cv2.getRotationMatrix2D((cX, cY), -angle, 1.0)
    cos = np.abs(M[0, 0])
    sin = np.abs(M[0, 1])

    # 計算影象的新邊界尺寸
    nW = int((h * sin) + (w * cos))
    nH = int((h * cos) + (w * sin))

    # 調整旋轉矩陣
    M[0, 2] += (nW / 2) - cX
    M[1, 2] += (nH / 2) - cY
    self.output_img =  cv2.warpAffine(image, M, (nW, nH),flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)

  def to_straighten(self): # 拉正圖片    
    
    # 獲取圖片旋轉角度
    gray = cv2.cvtColor(self.output_img, cv2.COLOR_BGR2GRAY)
    gray = cv2.bitwise_not(gray)
    thresh = cv2.threshold(gray, 0, 255,
        cv2.THRESH_BINARY | cv2.THRESH_OTSU)[1]
    coords = np.column_stack(np.where(thresh > 0))
    
    # 旋轉
    self.to_rotate(self.output_img, cv2.minAreaRect(coords)[-1])
  
  def to_add_contrast(self, alpha = 1.5, beta = 0): # 增加對比度
    '''
    :param alpha: int 當alpha > 0 提高對比，反之則降低。
    :param beta: int 當beta > 0 提高亮度，反之則降低。
    '''
    self.output_img = self.output_img * float(alpha) + beta
    self.output_img[self.output_img > 255] = 255
    self.output_img = np.round(self.output_img)
    self.output_img = self.output_img.astype(np.uint8)
  
  def to_sharpen(self, kernel_idx = 3): # 增加銳利度
    '''
    :param kernel_idx: int 選擇0~3不同的kernel進行銳化，越高越銳利。
    kernel原理：https://makerpro.cc/2019/06/the-convolution-of-opencv/
    常用kernel：https://en.wikipedia.org/wiki/Kernel_(image_processing)
    '''
    kernel_strategy = [
      [[0, -0.5, 0], [-0.5, 3, -0.5], [0, -0.5, 0]],
      [[0, -1, 0], [-1, 5, -1], [0, -1, 0]],
      [[-1, -1, -1], [-1, 8, -1], [-1, -1, 0]],
      [[-1, -1, -1], [-1, 9, -1], [-1, -1, -1]],
    ]
    kernel = np.array(kernel_strategy[kernel_idx])
    self.output_img = cv2.filter2D(self.output_img, -1, kernel)
  
  def to_resize(self): # 反轉圖片顏色
    length = self.output_img.shape[1]
    width = self.output_img.shape[0]
    self.output_img = cv2.resize(self.output_img, (2160, int(round(10 * width * 2160 / length) / 10)), interpolation = cv2.INTER_CUBIC)
    
  def to_reverse_color(self): # 反轉圖片顏色
    self.output_img = 255 - self.output_img
  
  def to_denoising(self): # 圖片降噪(處理灰階圖片會報錯)
    self.output_img = cv2.fastNlMeansDenoisingColored(self.output_img)  
    
  def to_filtering(self): # 圖片平滑化
    self.output_img = cv2.blur(self.output_img, (1, 1))

  def is_blackbased_image(self): # 判斷圖片是否為黑底圖片
    gray_img = cv2.cvtColor(self.input_img, cv2.COLOR_BGR2GRAY) # 取得輸入的圖像灰階
    histr = cv2.calcHist([gray_img],[0],None,[256],[0, 256]) # 計算圖像的顏色分佈
    return np.argmax(histr) <= (255 // 2) # 像素顏色最集中在0~127表示圖像整體偏黑，128~255則反之

  def get_img(self): # 獲取圖片
    return cv2.cvtColor(self.output_img, cv2.COLOR_BGR2RGB)
  
  def save_img(self, file_name = 'output'): # 儲存圖片
    cv2.imwrite(f'{file_name}.png', self.output_img)
  
  def show_img(self): # 顯示圖片
    cv2.namedWindow('Image', cv2.WINDOW_NORMAL)
    cv2.imshow('Image', self.output_img)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

if __name__ == "__main__":
    # transformer = IMG_preprocessing("C:/Users/NCKU/Downloads/python/1026_10907_1_000012.jpg")
    # transformer = IMG_preprocessing("C:/Users/NCKU/Downloads/python/ScreenShot_20201220155055.png")
    transformer = IMG_preprocessing("C:/Users/NCKU/Downloads/python/ScreenShot_20201220155055.png")
    # transformer.to_straighten()
    if transformer.is_blackbased_image(): 
        transformer.to_reverse_color() # 若為黑底則反轉圖片顏色
    transformer.to_denoising()
    # transformer.to_grayscale()
    transformer.to_add_contrast(alpha = 1)
    # transformer.to_thresholding(is_inverse=False)
    # transformer.to_sharpen()
    transformer.to_filtering()
    transformer.to_resize()
    
    transformer.save_img()
    # transformer.show_img()