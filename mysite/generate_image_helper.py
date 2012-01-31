# -*- coding: utf-8 -*

from pngcanvas import PNGCanvas

def generate_image(color_value):
    """根据颜色生成纯色图片，返回图片数据"""
    width = 300
    height = 300
    
    r = color_value[1:3]
    g = color_value[3:5]
    b = color_value[5:7]
    bgcolor=[int(r, 16), int(g, 16), int(b, 16), 0xff]
    img = PNGCanvas(width, height, bgcolor=bgcolor)

    return img.dump()

if __name__ == '__main__':
    data = generate_image("#74de1b")
    f = open("test.png", "wb")
    f.write(data)
    f.close()