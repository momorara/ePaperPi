#!/usr/bin/python
"""
描画領域はライブラリの関係で以下となる
0,0,290,127
ePaper のためのライブラリです。 
オリジナルのライブラリはjairoshさんの https://github.com/jairosh/raspberrypi-ssd1680/tree/master です。
 こちらは 「WeAct Studio 2.13" three-color e-paper display」用のものですが、 
 これを　WeAct Studio 2.9 白黒 用に改造したものになります。

ライセンスについては、オリジナルがGNU General Public License v3.0ですので、
本プログラムもGNU General Public License v3.0となります。

2024/07/08
ライブラリの名前をep_libとした
関数の名前も短くする。
mainから呼ぶときは text() だけで呼べるが、
importしたときは ep_lib.text() とする

2024/12/09  ePaperを書いた後i2cがおかしくなるので、i2cをリセットするとした
2025/01/10  RPi.GPIOを使わない方式とした
            ドライバーの都合なのか物理的には 128*296 のはずだが、128*293 の表示領域となります。
2025/01/17  bdfparserを使わない

2025/01/18
もとのoPaperのライブラリはbitmapフォントを使用するもので、bdfparserを使うものとなっている。
それだと、pipでのインストールが必要となりbookwormでは仮想環境が必要となる
そのためbdfparserを使わない方法として、TrueTypeのみを使うこととした。
しかし、TrueTypeをつかって、元のライブラリと共存させようとするとePaperの縦横がおかしくなる。
そこで、TrueTypeを使う場合は、ImageDraw.Draw(image)上の領域に文字と図形を全て書きePaperに
転送することで、表示することとする。
なので、文字も図形もImageDraw クラスのメソッドを使うことにする。
ただし、ePaperの初期化、転送のみ元のライブラリを使うこととなる。
"""

import raspberrypi_epd
# import RPi.GPIO as GPIO
import numpy as np
# from bdfparser import Font
import time
import random
import os
import time
from PIL import Image, ImageDraw, ImageFont

# Ejemplo de conexion
# BUSY          GPIO4
# RES           GPIO17
# D/C           GPIO27
# CS            GPIO22
# SCK           GPIO11 (SPI0 SCK)
# SDATA         GPIO10 (SPI0 MOSI)
# GND
# VCC

# GPIO.setmode(GPIO.BCM)
busy_gpio, reset_gpio, dc_gpio, cs_gpio = 4,17,27,22
display = raspberrypi_epd.WeAct213(busy=busy_gpio, reset=reset_gpio, dc=dc_gpio, cs=cs_gpio)
display.init()

# path = '/home/pi/ePaperPi/'  # cronで起動するには絶対パスが必要

# TrueTypeイメージを書く領域を確保
def image_set():
    # ビットマップ画像のサイズ
    image_width = 292
    image_height = 128
    # 新しい白黒画像を作成（モード1）
    image = Image.new("1", (image_width, image_height), 1)  # 1は白、0は黒
    # 描画用のオブジェクトを作成
    draw = ImageDraw.Draw(image)
    return draw,image

def font_set(font,font_size):
    # font : 明朝体=min ゴシック=gos min以外はゴシックになります
    font_path = '/usr/share/fonts/truetype/fonts-japanese-gothic.ttf'
    if font == "min":
        font_path = '/usr/share/fonts/truetype/fonts-japanese-mincho.ttf' 
    # フォントを読み込む
    font = ImageFont.truetype(font_path, font_size)
    # return font_path,font_size,font
    return font

# 画面を白くクリアする
def clear_w(draw):
    draw.rectangle((0, 0, 292, 127), outline="white", fill="white")
    display.init()
    display.set_rotation(90)
    display.fill(raspberrypi_epd.Color.WHITE)
    display.refresh(False)
    display.write_buffer()

# 画面を黒くクリアする
def clear_b(draw):
    draw.rectangle((0, 0, 292, 127), outline="black", fill="black")
    display.init()
    display.set_rotation(90)
    display.fill(raspberrypi_epd.Color.BLACK)
    display.refresh(False)
    display.write_buffer()

# バッファの内容をクリア
def clear_buffer():
    display.init()
    display.set_rotation(90)
    display.fill(raspberrypi_epd.Color.WHITE)
    # display.refresh(False)

# バッファの内容をePaperに書く
def write_buffer():
    display.write_buffer()

# ePaperライブラリを終了
# これをしないで、再起動するとワーニングが出る。
def close():
    display.close()
    # GPIO.cleanup()
    # ePaperを書いた後i2cがおかしくなるので、i2cをリセットする
    os.system("sudo rmmod i2c_bcm2835")
    os.system("sudo modprobe i2c_bcm2835")

"""
# # ビットマップフォントを設定する
# def set_font(n):
#     if n == 1:display.set_font(path + 'fonts/spleen-8x16.bdf')
#     if n == 2:display.set_font(path + 'fonts/luBS14.bdf')
#     if n == 3:display.set_font(path + 'fonts/helvB14.bdf')
#     # font-bitmapに矛盾がありwarningが出ますが、表示します。
#     # fontの種類により表示位置がずれます。

#文字を書く
def text(text,x,y,set):
    # 長い文字列を表示する場合、表示域をはみ出すとエラーになります。
    display.draw_text(text, x+3, y, raspberrypi_epd.Color.BLACK)
    if set == 1:
        display.write_buffer() # ePaperに表示

# # ビットマップ画像のサイズ
# image_width = 128
# image_height = 296
# # 新しい白黒画像を作成（モード1）
# image = Image.new("1", (image_width, image_height), 1)  # 1は白、0は黒
# # 描画用のオブジェクトを作成
# draw = ImageDraw.Draw(image)

# def text(text,x,y,font,size,set):
#     # ビットマップ画像のサイズ
#     image_width = 128
#     image_height = 296
#     # 新しい白黒画像を作成（モード1）
#     image = Image.new("1", (image_width, image_height), 1)  # 1は白、0は黒
#     # 描画用のオブジェクトを作成
#     draw = ImageDraw.Draw(image)
#     if font=="gothic":
#         font_path = '/usr/share/fonts/truetype/fonts-japanese-gothic.ttf'
#     else:
#         font_path = '/usr/share/fonts/truetype/fonts-japanese-mincho.ttf' 
#     # フォントを読み込む
#     font_size = size
#     font = ImageFont.truetype(font_path, font_size) 
#     japanese_text = text
#     text_position = (x, y)
#     draw.text(text_position, japanese_text, font=font, fill=0)  # 0は黒
#     BorW = 0
#     bmp_img(x,y,image,BorW,set)
#     if set == 1:
#         display.write_buffer() # ePaperに表示


# 点を書く
def pixel(x,y,color,set):
    if color == 'B':
        display.draw_pixel( x+3, y, raspberrypi_epd.Color.BLACK)
    if color == 'W':
        display.draw_pixel( x+3, y, raspberrypi_epd.Color.WHITE)
    if set == 1:
        display.init()
        display.write_buffer() # ePaperに表示

# 線を書きます。
def line(x1,y1,x2,y2,color,set):
    if color == 'B':
        display.draw_line( x1+3,y1,x2+3,y2, raspberrypi_epd.Color.BLACK)
    if color == 'W':
        display.draw_line( x1+3,y1,x2+3,y2, raspberrypi_epd.Color.WHITE)
    if set == 1:
        display.write_buffer() # ePaperに表示

# 円を書きます。
def circle(x,y,r,color,set):
    if color == 'B':
        display.draw_circle( x+3, y, r,raspberrypi_epd.Color.BLACK)
    if color == 'W':
        display.draw_circle( x+3, y, r,raspberrypi_epd.Color.WHITE)
    if set == 1:
        display.write_buffer() # ePaperに表示

# 四角を書きます。
def rectangle(x1,y1,x2,y2,color,set):
    # 四角のみx2,y2はx1,y1からの増分なので、変換する
    xw = x2 - x1
    yw = y2 - y1
    if color == 'B':
        display.draw_rectangle( x1+3,y1,xw,yw, raspberrypi_epd.Color.BLACK)
    if color == 'W':
        display.draw_rectangle( x1+3,y1,xw,yw, raspberrypi_epd.Color.WHITE)
    if set == 1:
        display.write_buffer() # ePaperに表示

# ビットマップファィルを描画
def bmp(x,y,path,BorW,set):
    # ビットマップファィルを読み込み bmp_img に渡す
    image = Image.open(path)
    bmp_img(x,y,image,BorW,set)
"""
# ビットマップイメージを描画
def ep_draw(x,y,image,BorW,set):
    y=y+3
    # x,yの位置にpathの示すビットマップファィルを描画
    # BorW 0:ビットをそのまま　1:ビットを反転して描画
    # set 0:バッファに書くだけ　1:ePaperに書く

    # 画面左上を0,0として、長い方を横:x、短い方を縦:yとする。
    # ビットマップの表示は画像のサイズ、表示位置、ePaperのバッファ領域を考慮して表示する必要がある
    # はみ出した場合は、描画されないか、エラーとなる
    # 290*128以内のビットマップ画像で、モノクロのみ対応

    # image = Image.open(path)
    # 画像の大きさを取得
    width, height = image.size
    print(f"width: {width}, height: {height}")
    # 読み込んだ画像の大きさ
    HEIGHT = 128
    WIDTH  = 296
    HEIGHT = height
    WIDTH  = width

    # 画像データの取得
    image_data = np.array(image)

    # # ディスプレイバッファを初期化
    # display.fill(raspberrypi_epd.Color.WHITE)

    display.set_rotation(0)
    dx = x # 画像描画位置を画面左上を0,0としての位置を変更する
    dy = HEIGHT -128 + y # y軸は左下が0なので変換が必要
    # 画像データをディスプレイバッファに書き込み
    for x in range(WIDTH):
        for y in range(HEIGHT):
            
            # ePaperのデフォルトが縦長な画面のため
            y1 = HEIGHT -1 - y
            # print(y,x,y1)
            if image_data[y1, x] == BorW:  # 黒ピクセル
                display.draw_pixel(y+3-dy, x+3+dx, raspberrypi_epd.Color.BLACK)
                # draw_pixel(x,y,"B",0)
            else:  # 白ピクセル
                # print(y+3-dy,x+3+dx)
                display.draw_pixel(y+3-dy, x+3+dx, raspberrypi_epd.Color.WHITE)
                # draw_pixel(x,y,"W",0)  
    if set == 1:
        display.write_buffer()  # ePaperに表示


def main():
    # print("画面を初期化して、黒くする。")
    # clear_b()

    print("画面を初期化して、白くする。")
    draw,image = image_set()
    clear_w(draw)

    draw.text((0, 0) ,"日本語　ゴシック", font=font_set("gos",24) ,fill=0)  # 0は黒
    draw.text((0, 26) ,"日本語　明朝", font=font_set("min",30) ,fill=0)  # 0は黒
    draw.text((0, 57) ,"abcdefghijkl 0123456789", font=font_set("gos",20) ,fill=0)  # 0は黒
    draw.text((0, 77) ,"0123456789 abcdefghijkl", font=font_set("gos",24) ,fill=0)  # 0は黒
    draw.text((0, 102) ,"!#$%&'()+*<>?/.,", font=font_set("gos",20) ,fill=0)  # 0は黒
    ep_draw(0,0,image,0,1)
    time.sleep(1)
    # image_set()
    clear_w(draw)


    draw.text((0, 0),"test random 3000 pixels", font=font_set("gos",24) ,fill=0)
    draw.rectangle((0, 30, 291, 127), outline="black", fill="white")
    for i in range(3000):
        x = random.randint(0, 291)
        y = random.randint(30, 127)
        draw.point((x, y), fill="black")
    write_buffer()
    ep_draw(0,0,image,0,1)
    time.sleep(1)
    clear_w(draw)


    draw.text((0, 0),"test random 80 line", font=font_set("gos",24) ,fill=0)
    draw.rectangle((0, 30, 291, 127), outline="black", fill="white")
    for i in range(80):
        x1 = random.randint(0, 291)
        y1 = random.randint(30, 127)
        x2 = random.randint(0, 291)
        y2 = random.randint(30, 127)
        draw.line((x1,y1,x2,y2), fill="black")
    write_buffer()   
    ep_draw(0,0,image,0,1)
    time.sleep(1)
    clear_w(draw)

    draw.text((0, 0),"ttest random 60 circles", font=font_set("gos",24) ,fill=0)
    draw.rectangle((0, 30, 291, 127), outline="black", fill="white")
    for i in range(60):
        x1 = random.randint(5, 270)
        y1 = random.randint(30, 97)
        r = random.randint(3, 30)
        draw.ellipse((x1, y1, x1+r ,y1+r), outline="black", fill="white")
    write_buffer()   
    ep_draw(0,0,image,0,1)
    time.sleep(1)
    clear_w(draw)

    # 既存の画像を開く 白黒画像に限る
    bitmap = Image.open("bmp/checker1.bmp")
    draw.bitmap((0, 0), bitmap, fill=None)
    write_buffer()   
    ep_draw(0,0,image,0,1)
    time.sleep(1)
    clear_w(draw)

    bitmap = Image.open("bmp/checker2.bmp")
    draw.bitmap((0, 0), bitmap, fill=None)
    write_buffer()   
    ep_draw(0,0,image,0,1)
    time.sleep(1)
    clear_w(draw)

    bitmap = Image.open("bmp/1bpp41.bmp")
    draw.bitmap((0, 0), bitmap, fill=None)
    write_buffer()   
    ep_draw(0,0,image,0,1)
    time.sleep(1)
    clear_w(draw)

    bitmap = Image.open("bmp/Mountain_290x128wb.bmp")
    draw.bitmap((0, 0), bitmap, fill=None)
    write_buffer()   
    ep_draw(0,0,image,0,1)
    time.sleep(3)
    clear_w(draw)


if __name__ == '__main__':
    main()
