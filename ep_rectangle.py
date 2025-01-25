#!/usr/bin/python

import ep_lib
import random

def main():

    print("画面を初期化して、白くする。")
    draw,image = ep_lib.image_set()
    ep_lib.clear_w(draw)

    draw.text((0, 0),"test random 40 rectangles", font=ep_lib.font_set("gos",22) ,fill=0)
    draw.rectangle((0, 30, 291, 127), outline="black", fill="white")

    for i in range(40):
        x1 = random.randint(0, 270)
        y1 = random.randint(30, 120)
        x2 = x1 + random.randint(5, 30)
        y2 = y1 + random.randint(5, 30)
        if x2 > 290:
            x1 = 290
        if y2  > 127:
            y2 = 127
        if y2 % 5 != 0:
            draw.rectangle((x1,y1,x2,y2), outline="black", fill="white", width=1)
        else:
            draw.rectangle((x1,y1,x2,y2), outline="white", fill="black", width=1)
    ep_lib.write_buffer()
    ep_lib.ep_draw(0,0,image,0,1)
    
    

if __name__ == '__main__':
    main()
