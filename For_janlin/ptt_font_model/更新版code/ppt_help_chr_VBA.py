# -*- coding: UTF-8 -*-
from PIL import Image
from win32com.client import DispatchEx
from win32gui import GetTextExtentPoint32, SelectObject, LOGFONT, CreateDC, CreateCompatibleBitmap, CreateFontIndirect, GetDC
from win32print import GetDeviceCaps
import os
import psutil

# 輸出路徑
output = 'D:/ppt_help/pptx/'
# 完全空白簡報檔路徑
ppt_file = "C:/Users/USER/pywork2/ppt_help/Text_shape.pptx"
# 文字檔路徑
text_file = 'C:/Users/USER/pywork2/ppt_help/word_text.txt'
# 最大寬度
maxwidth = 1800
# 最大高度
maxheight = 1800


def killtask():  # 強制關閉ppt.exe
    for process in psutil.process_iter():
        if process.name() == "POWERPNT.EXE":
            process.kill()


def merge_to_tiff(imgpath, fname) -> None:  # jpg to tiff
    filenames = os.listdir(imgpath)
    sortedfile = []
    for f in filenames:
        k = f.replace("投影片", "")
        k = k.replace(".TIF", "")
        sortedfile.append([f, int(k)])
    sortedfile.sort(key=lambda x: x[1])  # 排序

    for n in range(len(sortedfile)):
        filenames[n] = sortedfile[n][0]
    imgs = [Image.open("{}{}".format(imgpath, filename))
            for filename in filenames]
    # 如果圖片小於2張 則直接轉 否則壓縮
    if len(imgs) > 1:
        imgs[0].save("{}{}.tif".format(output, fname), compression="tiff_deflate",
                     save_all=True, append_images=imgs[1:])
    else:
        imgs[0].save("{}{}.tif".format(output, fname))


def init_powerpoint():

    powerpoint = DispatchEx("PowerPoint.Application")
    powerpoint.Visible = True    # 为了便于查阅PPT工作情况，这里设置为可见
    powerpoint.DisplayAlerts = False   # 为了使工作不中断，忽略可能的弹出警告
    return powerpoint


def ppt_to_jpg(powerpoint, inputFileName, outputFileName, formatType=21):  # 存成tif
    deck = powerpoint.Presentations.Open(inputFileName)
    deck.SaveAs(outputFileName, formatType)  # formatType = 17 for ppt to tif
    deck.Close()


def muldiv(num, numerator, denominator):  # 估算字體高度
    k = float(num)
    k = float(k) * numerator
    k = float(k) / denominator
    return int(k)


def getlableSize(text, font, size, underline=False, strikeout=False, Italic=False, Bold=False, Shadow=False):
    tempdc = 0
    tempbmp = 0
    f = 0
    lf = LOGFONT()
    textsize = 0
    tempdc = CreateDC("DISPLAY", "", None)
    tempbmp = CreateCompatibleBitmap(tempdc, 1, 1)
    tempobj = SelectObject(tempdc, tempbmp)  # 設定套用
    lf.lfFaceName = font
    lf.lfHeight = muldiv(size, GetDeviceCaps(GetDC(0), 90), 72)
    lf.lfUnderline = underline
    lf.lfItalic = Italic
    lf.lfStrikeOut = strikeout
    # 後來發現 粗體和陰影並不會增加太多字體大小
    # if Bold or Shadow:
    #     lf.lfWeight = 800
    # else:
    #     lf.lfWeight = 400
    f = CreateFontIndirect(lf)
    tempobj = SelectObject(tempdc, f)  # 設定套用

    for chr in text:  # 將字體配合主程式呼叫送出
        textsize = GetTextExtentPoint32(tempdc, chr)
        yield textsize
    return 0, 0


def RGB(red, green, blue):  # RGB計算
    assert 0 <= red <= 255
    assert 0 <= green <= 255
    assert 0 <= blue <= 255
    return red + (green << 8) + (blue << 16)


#主程式(檔名(預設 = "test"),字體(預設 = "標楷體"),底線,刪除線,斜體,粗體,陰影,文字外框(預設 = False),文字外框顏色,文字顏色(預設 = 黑色))
def tiffcreate(filename="test", font="kaiu", underline=False, strikeout=False, Italic=False, Bold=False, Shadow=False, textlinevis=False, textlinecolor=RGB(0, 0, 0), textfillcolor=RGB(0, 0, 0)):

    PPTApp = DispatchEx("PowerPoint.Application")
    PPTApp.Visible = True    # 为了便于查阅PPT工作情况，这里设置为可见
    PPTApp.DisplayAlerts = False   # 为了使工作不中断，忽略可能的弹出警告

    # 開啟完全空白的ppt
    PPTpresentation = PPTApp.Presentations.Open(ppt_file)

    layout = PPTpresentation.Designs(1).SlideMaster.CustomLayouts(1)
    PPTpresentation.Slides.AddSlide(1, layout)
    # 設定ppt大小 頁面大小與實際像素有誤差
    PPTpresentation.PageSetup.SlideWidth = maxwidth * \
        0.74988972209969122187913542126158
    PPTpresentation.PageSetup.SlideHeight = maxheight * \
        0.74988972209969122187913542126158
    PPTSlide1 = PPTpresentation.Slides(1)
    PPTSlide1.Name = "1"
    with open(text_file, 'r', encoding='utf-8') as f:
        testchr = f.read().replace('\n', ' ').split(' ')
    # 測試用 符號測試
    # testtext = "! \" # $ % & ' ( ) * + , - . / 0 1 2 3 4 5 6 7 8 9 : ; < = > ? @ A B C D E F G H I J K L M N O P Q R S T U V W X Y Z [ \ ] ^ _ ` a b c d e f g h i j k l m n o p q r s t u v w x y z { | } ~ ˇ “ ” ‧ ′ ‵ ※ € 、 。 〈 〉 《 》 「 」 『 』 【 】 〒 〔 〕 〝 〞 ㄦ 丐 丑 且 上 下 不 与 丐 丑 且 丕 世 丘"
    # 測試用 快速測試
    # testtext = "! \" # $ % & '"
    # testchr = testtext.split(" ")
    # ppt中的座標和實際座標不同 這裡以ppt座標為主
    # 基礎橫軸調整 影響座標生成
    bxmut = 1.322
    # 基礎縱軸調整 影響座標生成
    bymut = 1.353
    # 基礎橫軸座標
    basicx = 80
    # 基礎縱軸座標
    basicy = 80
    if Italic:
        bxmut = 1.33
    if font == "kaiu":  # 標楷體
        # 應每增加一個字元就擁有些微的誤差,需要累計型的調整
        # 累計橫軸調整
        xat = 0.0172
        if Bold or underline or Shadow:
            bxmut = 1.325
    elif font == "Microsoft JhengHei":  # 正黑體
        xat = 0.012
        if Italic:
            bxmut = 1.335
        if Bold or Shadow or strikeout == 1:
            bxmut = 1.325
        if underline:
            bxmut = 1.33
    elif font == "Microsoft YaHei":  # 雅黑體
        xat = 0.0165
        if Italic:
            xat = 0.025
        if Bold or Shadow:
            bxmut = 1.323
    elif font == "PMingLiU":  # 新細明體
        xat = 0.0165
        if Bold or underline or Shadow:
            bxmut = 1.325
    xadd = xat / 36  # 一行大約36個字元
    yadd = 0.0173 / 18  # 一頁大約18行
    currentx = basicx
    currenty = basicy
    currentslide = 1
    xmut = bxmut
    ymut = bymut
    box = []
    # 啟用產生器
    g = getlableSize(testchr, font, 45, underline=underline,
                     strikeout=strikeout, Italic=Italic, Bold=Bold, Shadow=Shadow)
    for chr in testchr:
        # 呼叫生成器 同步產生對應字體
        # cx 字體寬度
        # cy 字體高度
        cx, cy = next(g)
        # 若生成器結束 則回傳0,0 跳出
        if cx == 0 and cy == 0:
            break
        tempx = currentx
        # 字寬+6 影響字元生成
        cx = cx + 6
        # 根據不同字形或字元作微調
        if font == "kaiu":

            if strikeout == 1 or Italic:
                cx = cx + 10

            if underline:
                if chr == "|":
                    cx = cx + 3
            if chr == "※":
                cx = cx + 3
            if chr == "/":
                cx = cx + 10
                if Bold or Shadow:
                    cx = cx + 7
            if chr == "\\":
                cx = cx + 10
                if Bold or Shadow:
                    cx = cx + 9
            if chr == "“":
                tempx = currentx
                currentx = currentx - cx - 5
                cx = cx * 2
            if chr == "”":
                cx = cx * 2
            if underline:
                if chr == "”" or chr == "“":
                    cx = cx + 10
        if font == "Microsoft JhengHei":
            # cx = cx + 6
            if strikeout == 1 or Italic:
                cx = cx + 12

                if chr == "※":
                    cx = cx + 8
                if chr == "》" or chr == "〒":
                    cx = cx + 4
            if chr == "/":
                cx = cx + 4
                if Bold or Shadow:
                    cx = cx + 7
            if chr == "\\":
                cx = cx + 4
                if Bold or Shadow:
                    cx = cx + 9
            if chr == "f" or chr == "r" or chr == "_" or chr == "|":
                cx = cx + 6
        if font == "Microsoft YaHei":
            cx = cx + 5
            if strikeout == 1 or Italic:
                cx = cx + 12

        if font == "PMingLiU":
            # cx = cx + 5
            if strikeout == 1 or Italic:
                cx = cx + 10
            elif Bold or Shadow:
                cx = cx + 4
            if chr == "/" or chr == "\\":
                cx = cx + 10
            if underline:
                if chr == "|":
                    cx = cx + 6

        if currentx+cx+12 >= PPTpresentation.PageSetup.SlideWidth:
            # 初始化 並換行
            currentx = basicx
            tempx = currentx
            currenty = currenty + 68
            xmut = bxmut
            ymut = ymut - yadd
        if currenty+68 >= PPTpresentation.PageSetup.SlideHeight:
            # 初始化
            currentx = basicx
            currenty = basicy
            currentslide = currentslide + 1
            PPTpresentation.Slides.AddSlide(currentslide, layout)
            PPTpresentation.PageSetup.SlideWidth = maxwidth * \
                0.74988972209969122187913542126158
            PPTpresentation.PageSetup.SlideHeight = maxheight * \
                0.74988972209969122187913542126158
            PPTSlide1 = PPTpresentation.Slides(currentslide)
            PPTSlide1.Name = "{}".format(currentslide)
            xmut = bxmut
            ymut = bymut
        # 生成一個矩形
        # 只有矩形中的字元擁有刪除線特效與變換文字外框等功能
        shape1 = PPTSlide1.Shapes.AddShape(
            Type=1, Left=currentx, Top=currenty, Width=cx, Height=cy)
        shape1.TextFrame.TextRange.Text = chr
        shape1.TextFrame.TextRange.Font.Size = 45
        shape1.TextFrame2.TextRange.ParagraphFormat.Alignment = 2
        shape1.TextFrame2.TextRange.Font.Strike = strikeout
        shape1.TextFrame.TextRange.Font.Underline = underline
        shape1.TextFrame.TextRange.Font.Shadow = Shadow
        shape1.TextFrame.TextRange.Font.Bold = Bold
        shape1.TextFrame.TextRange.Font.Italic = Italic
        shape1.TextFrame2.TextRange.Characters.Font.Fill.ForeColor.RGB = textfillcolor
        # 若需要顯現文字外框
        if textlinevis:
            shape1.TextFrame2.TextRange.Characters.Font.Line.Visible = True
            shape1.TextFrame2.TextRange.Characters.Font.Line.ForeColor.RGB = textlinecolor
        # 將矩形設定為 無填滿 無外框
        shape1.Fill.Visible = False
        shape1.Line.Visible = False
        # 根具字形或字元做版面微調
        if font == "kaiu":

            if chr == "”" or chr == "“":
                shape1.TextFrame2.TextRange.ParagraphFormat.Alignment = 1
                if Italic:
                    if chr == "”":
                        shape1.TextFrame2.TextRange.ParagraphFormat.Alignment = 2
                    else:
                        shape1.TextFrame2.TextRange.ParagraphFormat.Alignment = 3
                if strikeout == 1:
                    if chr == "“":
                        shape1.Left = currentx + 25
                        shape1.TextFrame2.TextRange.ParagraphFormat.Alignment = 3
                if underline:

                    if chr == "“":
                        shape1.TextFrame2.TextRange.ParagraphFormat.Alignment = 2
                        shape1.Left = currentx + 25
                    else:
                        shape1.Left = currentx - 5
                if strikeout == 1 and Italic:
                    if chr == "“":
                        shape1.Left = currentx + 27
            if Italic:
                if chr == "※":
                    shape1.TextFrame2.TextRange.ParagraphFormat.Alignment = 2
                if chr == "€":
                    shape1.TextFrame2.TextRange.ParagraphFormat.Alignment = 2
            if underline:
                if chr == ":" or chr == ";":
                    shape1.Left = currentx + 3
        if font == "Microsoft JhengHei":
            if chr == "”" or chr == "“":
                shape1.TextFrame2.TextRange.ParagraphFormat.Alignment = 2
            if underline:
                if chr == ":" or chr == ";":
                    shape1.Left = currentx + 5
            if Bold:
                if chr == "碧" or chr == "筵":
                    shape1.Left = currentx + 13
        if font == "Microsoft YaHei":
            if chr == "_":
                shape1.Left = currentx - 3
        # # 中文專用字形設定
        shape1.TextFrame.TextRange.Font.NameFarEast = font
        # 個別字元調整
        if chr == "“":
            box.append("{} {} {} {} {} {}".format(chr, int(round(tempx*xmut)), maxheight-(int(round((currenty+cy)*ymut))),
                                                  int(round((tempx+cx)*xmut)), maxheight-int(round(currenty*ymut)), currentslide-1))
            box.append("{} {} {} {} {} {}".format('\t', int(round((tempx+cx)*xmut)), maxheight-(int(round((currenty+cy)*ymut))),
                                                  int(round((tempx+cx)*xmut))+10, maxheight-int(round(currenty*ymut)), currentslide-1))
        # 紀錄該字元座標軸
        else:
            box.append("{} {} {} {} {} {}".format(chr, int(round(currentx*xmut)), maxheight-(int(round((currenty+cy)*ymut))),
                                                  int(round((currentx+cx)*xmut)), maxheight-int(round(currenty*ymut)), currentslide-1))
            # 生成空格座標軸
            box.append("{} {} {} {} {} {}".format('\t', int(round((currentx+cx)*xmut)), maxheight-(int(round((currenty+cy)*ymut))),
                                                  int(round((currentx+cx)*xmut))+10, maxheight-int(round(currenty*ymut)), currentslide-1))

        if font == "kaiu":
            if chr == "“":
                currentx = tempx
        currentx = currentx + cx + 12
        xmut = xmut + xadd
    g.close()  # 關閉生成器
    # 路徑做成
    pptxfullpath = os.path.join(output, "{}.pptx".format(filename))
    tiffullpath = os.path.join(output, "{}.jpg".format(filename))
    print(pptxfullpath)
    PPTpresentation.SaveAs(pptxfullpath)  # 存成ppt
    # 關閉
    PPTpresentation.close()

    # 再次初始化
    powerpoint = init_powerpoint()
    # 因應VBA函數 將路徑的/ 改為 \
    convertfullpath = tiffullpath.replace("/", "\\")
    # 生成jpg
    ppt_to_jpg(powerpoint, pptxfullpath, convertfullpath)

    imgfullpath = os.path.join(output, "{}/".format(filename))
    boxfullpath = os.path.join(output, "{}.box".format(filename))
    # 將jpg壓縮成tiff
    merge_to_tiff(imgfullpath, filename)
    # 生成box檔案
    with open(boxfullpath, 'w', encoding="UTF-8") as f:
        for item in box:
            f.write("%s\n" % item)
        f.close()
    # 因應VBA關閉不完全 直接kill 以節省記憶體
    killtask()


# 檔名(預設 = "test"),字體(預設 = "標楷體"),底線,刪除線,斜體,粗體,陰影,文字外框(預設 = False),文字外框顏色,文字顏色(預設 = 黑色)
# 呼叫方式 filename = String , font = String , underline,Italic,Bold,Shadow,textlinevis = Bool
# strikeout = int(0 或 1),textlinecolor,textfillcolor = RGB(red, green, blue)
tiffcreate(filename="chr_kaiu")
tiffcreate(filename="chr_kaiu_bold", font="kaiu", Bold=True)
tiffcreate(filename="chr_kaiu_Shadow", font="kaiu", Shadow=True)
tiffcreate(filename="chr_kaiu_Italic", font="kaiu", Italic=True)
tiffcreate(filename="chr_kaiu_strikeout", font="kaiu", strikeout=1)
tiffcreate(filename="chr_kaiu_underline", font="kaiu", underline=True)
tiffcreate(filename="chr_kaiu_bold_shadow_tlblack_tfwhite", font="kaiu", Bold=True,
           Shadow=True, textlinevis=True, textlinecolor=RGB(0, 0, 0), textfillcolor=RGB(255, 255, 255))
tiffcreate(filename="chr_kaiu_bold_shadow_tlwhite", font="kaiu", Bold=True,
           Shadow=True, textlinevis=True, textlinecolor=RGB(255, 255, 255))


tiffcreate(filename="chr_Microsoft JhengHei")
tiffcreate(filename="chr_Microsoft JhengHei_bold",
           font="Microsoft JhengHei", Bold=True,)
tiffcreate(filename="chr_Microsoft JhengHei_Shadow",
           font="Microsoft JhengHei", Shadow=True)
tiffcreate(filename="chr_Microsoft JhengHei_Italic",
           font="Microsoft JhengHei", Italic=True)
tiffcreate(filename="chr_Microsoft JhengHei_strikeout",
           font="Microsoft JhengHei", strikeout=1)
tiffcreate(filename="chr_Microsoft JhengHei_underline",
           font="Microsoft JhengHei", underline=True)
tiffcreate(filename="chr_Microsoft JhengHei_bold_shadow_tlblack_tfwhite", font="Microsoft JhengHei", Bold=True,
           Shadow=True, textlinevis=True, textlinecolor=RGB(0, 0, 0), textfillcolor=RGB(255, 255, 255))
tiffcreate(filename="chr_Microsoft JhengHei_bold_shadow_tlwhite", font="Microsoft JhengHei", Bold=True,
           Shadow=True, textlinevis=True, textlinecolor=RGB(255, 255, 255))


tiffcreate(filename="chr_Microsoft YaHei")
tiffcreate(filename="chr_Microsoft YaHei_bold",
           font="Microsoft YaHei", Bold=True,)
tiffcreate(filename="chr_Microsoft YaHei_Shadow",
           font="Microsoft YaHei", Shadow=True)
tiffcreate(filename="chr_Microsoft YaHei_Italic",
           font="Microsoft YaHei", Italic=True)
tiffcreate(filename="chr_Microsoft YaHei_strikeout",
           font="Microsoft YaHei", strikeout=1)
tiffcreate(filename="chr_Microsoft YaHei_underline",
           font="Microsoft YaHei", underline=True)
tiffcreate(filename="chr_Microsoft YaHei_bold_shadow_tlblack_tfwhite", font="Microsoft YaHei", Bold=True,
           Shadow=True, textlinevis=True, textlinecolor=RGB(0, 0, 0), textfillcolor=RGB(255, 255, 255))
tiffcreate(filename="chr_Microsoft YaHei_bold_shadow_tlwhite", font="Microsoft YaHei", Bold=True,
           Shadow=True, textlinevis=True, textlinecolor=RGB(255, 255, 255))

tiffcreate(filename="chr_PMingLiU")
tiffcreate(filename="chr_PMingLiU_bold", font="PMingLiU", Bold=True,)
tiffcreate(filename="chr_PMingLiU_Shadow", font="PMingLiU", Shadow=True)
tiffcreate(filename="chr_PMingLiU_Italic", font="PMingLiU", Italic=True)
tiffcreate(filename="chr_PMingLiU_strikeout", font="PMingLiU", strikeout=1)
tiffcreate(filename="chr_PMingLiU_underline", font="PMingLiU", underline=True)
tiffcreate(filename="chr_PMingLiU_bold_shadow_tlblack_tfwhite", font="PMingLiU", Bold=True,
           Shadow=True, textlinevis=True, textlinecolor=RGB(0, 0, 0), textfillcolor=RGB(255, 255, 255))
tiffcreate(filename="chr_PMingLiU_bold_shadow_tlwhite", font="PMingLiU", Bold=True,
           Shadow=True, textlinevis=True, textlinecolor=RGB(255, 255, 255))
