
import PIL
from PIL import Image, ImageDraw, ImageEnhance, ImageFilter
import os
from math import asin, sin
import pygame

class Cutter:
    @staticmethod
    def similar(c1, c2):
        [r1, g1, b1] = c1
        [r2, g2, b2] = c2
        return 100 - (abs(r1-r2)/255*100 + abs(g1-g2)/255*100 + abs(b1-b2)/255*100) / 3
    
    @staticmethod
    def load_img(file):
        img = Image.open(file)
        return img
    
    @staticmethod
    def cut_bg(img:Image.Image, bright, blur):
        img = img.filter(ImageFilter.GaussianBlur(radius=blur)) # 3
        img = ImageEnhance.Brightness(img).enhance(bright) # 1.5
        
        img = ImageEnhance.Contrast(img).enhance(30.0)
        img = ImageEnhance.Sharpness(img).enhance(5.0)
        img = img.convert('RGB')
        # display(img)

        pix = img.load()
        w, h, = img.width, img.height
        for r in range(h):
            for c in range(w):
                [R, G, B] = pix[c, r]
                pix[c, r] = (0,0,0) if (R+G+B)/3 < 190 else (255,255,255)
        
        pix = img.load()
        w = img.width
        h = img.height

        screen = [[0 for x in range(w)] for y in range(h)]
        screen[0][0] = 1

        # сверху вниз, слева направо
        for r in range(h):
            for c in range(w):
                if (c>0 and screen[r][c-1]==1) or (r>0 and screen[r-1][c]==1):    
                    if Cutter.similar([255,255,255], pix[c, r]) > 0:
                        screen[r][c] = 1
        # снизу вверх, справа налево
        for r in range(h)[::-1]:
            for c in range(w)[::-1]:
                if (c<w-1 and screen[r][c+1]==1) or (r<h-1 and screen[r+1][c]==1):    
                    if Cutter.similar([255,255,255], pix[c, r]) > 95:
                        screen[r][c] = 1
        for r in range(h):
            for c in range(w)[::-1]:
                if (c<w-1 and screen[r][c+1]==1) or (r>0 and screen[r-1][c]==1):    
                    if Cutter.similar([255,255,255], pix[c, r]) > 95:
                        screen[r][c] = 1
        for r in range(h)[::-1]:
            for c in range(w):
                if (c>0 and screen[r][c-1]==1) or (r<h-1 and screen[r+1][c]==1):    
                    if Cutter.similar([255,255,255], pix[c, r]) > 95:
                        screen[r][c] = 1

        return screen
    
    @staticmethod
    def dist(x1,y1, x2,y2):
        return ((x1-x2)**2 + (y1-y2)**2)**0.5
    
    @staticmethod
    def drop_coin2(base_screen, pos=[0, 0], radius=0):
        w = len(base_screen[0])
        h = len(base_screen)
        [px, py] = pos
        for r in range(h):
            for c in range(w):
                if Cutter.dist(px,py, c,r) <= radius:
                    base_screen[r][c] = 1
        return base_screen
    
    @staticmethod
    def find_vertexes(screen, add_del_r):
        vertexes = []
        w = len(screen[0])
        h = len(screen)

        ct = 0

        def find_money(screen):
            nonlocal vertexes, ct
            print(ct)
            ct += 1
            for r in range(h):
                for c in range(w):
                    if screen[r][c] == 0:
                        # найти координаты хорд
                        H = 35
                        dy = 12
                        coords = [[[c, r+dy], [c, r+dy]], [[c, r+dy+H], [c, r+dy+H]]]
                        for i in range(2):
                            for _ in range(c)[::-1]:
                                if screen[coords[i][0][1]][coords[i][0][0]] == 0: coords[i][0][0] -= 1
                                else: break
                            for _ in range(c, w)[::-1]:
                                if screen[coords[i][1][1]][coords[i][1][0]] == 0: coords[i][1][0] += 1
                                else: break

                        radius = Cutter.calc_radius(coords[0], coords[1], H)
                        vertexes.append([
                            (coords[0][0][0]+coords[0][1][0])/2-radius-1, r, radius+1
                        ])
                        screen = Cutter.drop_coin2(screen, [(coords[0][0][0]+coords[0][1][0])//2, int(r)+radius], radius+add_del_r)
                        # display(draw_screen(screen))
                        find_money(screen)
                        return screen
                    
        screen = find_money(screen)
        return vertexes
    
    @staticmethod
    def set_mask(img:Image.Image, screen):
        w = len(screen[0])
        h = len(screen)
        res_img = Image.new('RGBA', size=[w, h], color="#00000000")
        res_pix = res_img.load()
        img = img.convert('RGB')
        pix = img.load()
        for r in range(h):
            for c in range(w):
                if screen[r][c] == 0:
                    [R, G, B] = pix[c, r]
                    res_pix[c, r] = (R, G, B, 255)
        return res_img
    
    @staticmethod
    def calc_radius(line1, line2, H):
        w1 = line1[1][0] - line1[0][0]
        w2 = line2[1][0] - line2[0][0]
        
        c = (H**2 + ((w2-w1)/2)**2)**0.5
        c2 = (H**2 + (w2/2+w1/2)**2)**0.5

        angle = asin(H/c2)

        # radius = (c/2)/sin(angle)
        radius = (c/2)/(H/c2)
        return radius
    
    @staticmethod
    def cut_imgs(vertexes, base_img:Image.Image):
        path = 'src/imgs'
        file_list = os.listdir(path)
        for file in file_list:
            file_path = os.path.join(path, file)
            os.remove(file_path)

        res = []
        for i, (x, y, radius) in enumerate(vertexes):
            # img = Image.new('RGBA', size=[radius*2, radius*2], color="#00000000")
            img_ = base_img.crop([x, y, x+radius*2, y+radius*2])
            pix = img_.load()
            for r in range(img_.height):
                for c in range(img_.width):
                    if Cutter.dist(radius,radius, c,r) > radius+1:
                        pix[c, r] = (0,0,0,0)
            # imgs.append(img_)
            img_.save(f'src/imgs/{i}.png')
            res.append(f'src/imgs/{i}.png')
        return res

    @staticmethod
    def generate(file, bright, blur, add_del_r):
        img = Cutter.load_img(file)
        screen = Cutter.cut_bg(img, bright, blur)
        
        img = Cutter.set_mask(img, screen)
        vertexes = Cutter.find_vertexes(screen, add_del_r)
        res = Cutter.cut_imgs(vertexes, img)
        return res