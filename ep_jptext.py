#!/usr/bin/python
"""
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

import ep_lib
import time
from PIL import Image, ImageDraw, ImageFont

# # TrueTypeイメージを書く領域を確保
# def jp_image():
#     # ビットマップ画像のサイズ
#     image_width = 292
#     image_height = 128
#     # 新しい白黒画像を作成（モード1）
#     image = Image.new("1", (image_width, image_height), 1)  # 1は白、0は黒
#     # 描画用のオブジェクトを作成
#     draw = ImageDraw.Draw(image)
#     return draw,image

# def font_set(font,font_size):
#     # font : 明朝体=min ゴシック=gos min以外はゴシックになります
#     font_path = '/usr/share/fonts/truetype/fonts-japanese-gothic.ttf'
#     if font == "min":
#         font_path = '/usr/share/fonts/truetype/fonts-japanese-mincho.ttf' 
#     # フォントを読み込む
#     font = ImageFont.truetype(font_path, font_size)
#     # return font_path,font_size,font
#     return font


def main():

    print("画面を初期化して、白くする。")
    ep_lib.clear_w()

    """
    size=10
    set=1
    ep_lib.text("testtest",0,0,"gothic",size,1)
    ep_lib.text("123456",10,10,"gothic",size,1)
    ep_lib.text("abcdef",20,20,"gothic",size,1)
    ep_lib.text(")(&%$#)",30,30,"gothic",size,set)
    """
    
    # # ビットマップ画像のサイズ
    # image_width = 292
    # image_height = 128
    # # 新しい白黒画像を作成（モード1）
    # image = Image.new("1", (image_width, image_height), 1)  # 1は白、0は黒
    # # 描画用のオブジェクトを作成
    # draw = ImageDraw.Draw(image)
    draw,image = ep_lib.image_set()



    # # ゴシック
    # font_path = '/usr/share/fonts/truetype/fonts-japanese-gothic.ttf'
    # font_path,font_size,font = font_set("gos",32)
    # font = font_set("gos",16)
    # # フォントサイズ
    # font_size = 28
    # # 描画する日本語テキスト
    # japanese_text = "日本語　ゴシック"
    # フォントを読み込む
    # font = ImageFont.truetype(font_path, font_size)
    # テキストを画像に描画
    # font = font_set("gos",28)
    # text_position = (0, 0)  # テキストの位置（左上の座標）
    draw.text((0, 0) ,"日本語　ゴシック", font=ep_lib.font_set("gos",24) ,fill=0)  # 0は黒

    draw.text((0, 30) ,"日本語　明朝", font=ep_lib.font_set("min",30) ,fill=0)  # 0は黒

    draw.point((50, 800), fill="black")
    draw.point((51, 81), fill="black")
    draw.point((52, 82), fill="black")
    draw.line((20, 60, 160, 80), fill="black")

    x,y,BorW = 0,0,0
    # 画像イメージをePaperに描画
    ep_lib.ep_draw(x,y,image,BorW,1)

    draw.rectangle((200, 50, 250, 80), outline="black", fill="black")
    draw.ellipse((100, 60, 120 ,80), outline="black", fill="white")

    # ep_lib.rectangle(0,30,292,127,"B",1)
    # ep_lib.rectangle(30,0,127,292,"B",1)

    x,y,BorW = 0,0,0
    # 画像イメージをePaperに描画
    ep_lib.ep_draw(x,y,image,BorW,1)
    # ep_lib.rectangle(0,30,29,127,"B",1)
    # ep_lib.rectangle(30,0,127,292,"B",1)

    """
    # 明朝体
    font_path = '/usr/share/fonts/truetype/fonts-japanese-mincho.ttf'  
    # フォントサイズ
    font_size = 28
    # 描画する日本語テキスト
    japanese_text = "日本語　明朝"
    # フォントを読み込む
    font = ImageFont.truetype(font_path, font_size)
    # テキストを画像に描画
    text_position = (0, 40)  # テキストの位置（左上の座標）
    draw.text(text_position, japanese_text, font=font, fill=0)  # 0は黒

    x,y = 0,0
    BorW = 0
    # 画像イメージをePaperに描画
    ep_lib.bmp_img(x,y,image,BorW,1)

    time.sleep(2)

    # ゴシック
    font_path = '/usr/share/fonts/truetype/fonts-japanese-gothic.ttf'
    # フォントサイズ
    font_size = 22
    # 描画する日本語テキスト
    japanese_text = "0123456789 abcdefg ABCDEFG"
    # フォントを読み込む
    font = ImageFont.truetype(font_path, font_size)
    # テキストを画像に描画
    text_position = (0, 80)  # テキストの位置（左上の座標）
    draw.text(text_position, japanese_text, font=font, fill=0)  # 0は黒    

    # 明朝体
    font_path = '/usr/share/fonts/truetype/fonts-japanese-mincho.ttf'  
    # フォントサイズ
    font_size = 22
    # 描画する日本語テキスト
    japanese_text = "0123456789 abcdefg ABCDEFG"
    # フォントを読み込む
    font = ImageFont.truetype(font_path, font_size)
    # テキストを画像に描画
    text_position = (0, 104)  # テキストの位置（左上の座標）
    draw.text(text_position, japanese_text, font=font, fill=0)  # 0は黒

    ep_lib.bmp_img(x,y,image,BorW,1)

    """
    
    """

    # ゴシック
    font_path = '/usr/share/fonts/truetype/fonts-japanese-gothic.ttf'
    # 明朝体
    font_path = '/usr/share/fonts/truetype/fonts-japanese-mincho.ttf'

    # フォントサイズ
    font_size = 20

    # 描画する日本語テキスト
    japanese_text = "こんにちは、世界！"

    # 新しい白黒画像を作成（モード1）
    image = Image.new("1", (image_width, image_height), 1)  # 1は白、0は黒

    # 描画用のオブジェクトを作成
    draw = ImageDraw.Draw(image)

    # フォントを読み込む
    font = ImageFont.truetype(font_path, font_size)

    # テキストを画像に描画
    text_position = (0, 0)  # テキストの位置（左上の座標）
    draw.text(text_position, japanese_text, font=font, fill=0)  # 0は黒
    font_size = 30
    font = ImageFont.truetype(font_path, font_size)
    text_position = (0, 20)  # テキストの位置（左上の座標）
    draw.text(text_position, japanese_text, font=font, fill=0)  # 0は黒
    font_size = 36
    font = ImageFont.truetype(font_path, font_size)
    text_position = (0, 50)  # テキストの位置（左上の座標）
    japanese_text = "日本語表示できた"
    draw.text(text_position, japanese_text, font=font, fill=0)  # 0は黒

    x,y = 0,0
    BorW = 0
    # 画像イメージをePaperに描画
    ep_lib.bmp_img(x,y,image,BorW,1)

    time.sleep(3)
    # 描画した内容をクリア
    draw.rectangle([0, 0, image.width, image.height], fill='white')

    japanese_text = "日本語表示できた"
    draw.text(text_position, japanese_text, font=font, fill=0)  # 0は黒
    ep_lib.bmp_img(x,y,image,BorW,1)

    """

if __name__ == '__main__':
    main()
