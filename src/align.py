
import PIL
from PIL import Image, ImageDraw, ImageEnhance, ImageFilter, ImageOps
import os
import pygame

class AutoAlign:
    @staticmethod
    def convert_img(img:Image.Image):
        img = img.filter(ImageFilter.GaussianBlur(radius=0.9))
        img = img.convert('L').filter(ImageFilter.CONTOUR)
        img = ImageEnhance.Contrast(img).enhance(20.0)
        pix = img.load()
        for r in range(img.height):
            pix[0, r] = 255
            pix[-1, r] = 255
        for c in range(img.width):
            pix[c, 0] = 255
            pix[c, -1] = 255
        img = ImageOps.invert(img)
        return img


    @staticmethod
    def get_h_gradient(img:Image.Image):
        res = Image.new('RGB', size=[img.width, img.height])
        rpix = res.load()
        pix = img.load()
        mx = 255*img.width
        for r in range(img.height):
            sm = sum([pix[c, r] for c in range(img.width)])
            color = int(sm/mx*255)
            # for c in range(img.width):
            for c in range(3):
                rpix[c, r] = tuple([color]*3)
        return res
    

    @staticmethod
    def get_h_diff(img:Image.Image):
        # res = Image.new('RGB', size=[img.width, img.height])
        # rpix = res.load()
        pix = img.load()
        mx = 0
        start = int(img.height * 0.1)
        end = int(img.height * 0.9)
        for r in range(start, end):
            dif = abs(pix[2, r][0] - pix[2, r-1][0])
            if dif < 20: dif = 0
            color = tuple([dif]*3)
            if color[0] > mx:
                mx = color[0]
        
            # for c in range(img.width):
            #     rpix[c, r] = color
        return mx
        
    @staticmethod
    def get_angle(baseimg:pygame.Surface, a_start=-32, a_end=32):

        [w, h] = baseimg.get_size()
        pixel_data = pygame.image.tostring(baseimg, 'RGBA')
        baseimg = Image.frombytes('RGBA', (w, h), pixel_data)

        baseimg = baseimg.resize(size=[200,200])

        img = AutoAlign.convert_img(baseimg)
        optimal = [0, 0] # [max, angle]
        for a in range(a_start, a_end):
            rot_img = img.rotate(a, fillcolor="#000")
            n = AutoAlign.get_h_diff(AutoAlign.get_h_gradient(rot_img))
            if n > optimal[0]:
                optimal = [n, a]
        return optimal[1]
        # baseimg = baseimg.rotate(optimal[1])
        # return baseimg
