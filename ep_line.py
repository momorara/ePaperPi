#!/usr/bin/python

import ep_lib
import random

def main():

    print("画面を初期化して、白くする。")
    draw,image = ep_lib.image_set()
    ep_lib.clear_w(draw)

    draw.text((0, 0),"test random 80 lines", font=ep_lib.font_set("gos",24) ,fill=0)
    draw.rectangle((0, 30, 291, 127), outline="black", fill="white")

    for i in range(80):
        x1 = random.randint(0, 292)
        y1 = random.randint(30, 127)
        x2 = random.randint(0, 292)
        y2 = random.randint(30, 127)
        draw.line((x1,y1,x2,y2), fill="black")

    ep_lib.write_buffer()
    ep_lib.ep_draw(0,0,image,0,1)
    
    

if __name__ == '__main__':
    main()
