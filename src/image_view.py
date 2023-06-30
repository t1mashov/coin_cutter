import pygame
from PIL import Image

from ezzgui.views.base_view import BaseView
from ezzgui.views.view import MouseSensView

import math


class CircleLine:
    def __init__(self, win, imgView):
        self.win = win
        self.imgView = imgView
        [_, _, iw, ih] = [*self.imgView.getStart(), *self.imgView.getSize()]
        r = 10
        self.pos = [iw//2, ih//2, r*2, r*2]
        self.pressed = False
        self.radius = 50

    def isOnFocus(self, mpos):
        [ix, iy, iw, ih] = [*self.imgView.getStart(), *self.imgView.getSize()]
        [mx, my] = mpos
        [x, y, r2, _] = self.pos
        r = r2/2
        x += ix
        y += iy
        if x-r < mx < x+r and y-r < my < y+r:
            return True
        return False
    
    def passMouseEvents(self, events):
        for e in events:
            if e.type == pygame.MOUSEBUTTONDOWN:
                return e.button
        return None

    def draw(self):
        [x, y, r2, _] = self.pos
        [ix, iy, iw, ih] = [*self.imgView.getStart(), *self.imgView.getSize()]
        r = r2/2
        pygame.draw.ellipse(self.win, (250,250,250), [ix + x-r, iy + y-r, r*2,r*2])
        pygame.draw.ellipse(self.win, (0,0,0), [ix + x-r, iy + y-r, r*2,r*2], 1)

        radius = self.radius * self.imgView.resize
        pygame.draw.ellipse(self.win, (0,150,100), [ix + x-radius, iy + y-radius, radius*2, radius*2], 2)
        pygame.draw.ellipse(self.win, (100,255,100), [ix + x-radius-1, iy + y-radius-1, radius*2+2, radius*2+2], 2)
        ...

    def spawn(self, events, mpos, mpress):
        self.draw()

        if self.isOnFocus(mpos):
            b = self.passMouseEvents(events)
            if b == 1:
                self.pressed = True
        if not mpress[0]:
            self.pressed = False

        if self.pressed:
            [ix, iy, iw, ih] = [*self.imgView.getStart(), *self.imgView.getSize()]
            [mx, my] = mpos
            self.pos[0] = mx-ix
            self.pos[1] = my-iy

            if self.pos[0] < 0: self.pos[0] = 0
            if self.pos[1] < 0: self.pos[1] = 0
            if self.pos[0] > iw: self.pos[0] = iw
            if self.pos[1] > ih: self.pos[1] = ih
        ...


class DirLine:
    def __init__(self, win, imgView):
        self.win = win
        self.imgView = imgView
        [_, _, iw, ih] = [*self.imgView.getStart(), *self.imgView.getSize()]
        r = 5
        self.pos = [10, 10, r*2, r*2]
        self.pressed = False

    
    def draw(self):
        [ix, iy, iw, ih] = [*self.imgView.getStart(), *self.imgView.getSize()]
        [x, y, r2, _] = self.pos
        r = r2/2
        d = 1
        pygame.draw.rect(self.win, (255,100,100), [ix, iy + y-d, iw, d*2])
        pygame.draw.rect(self.win, (100,100,255), [ix + x-d, iy,d*2, ih])
        pygame.draw.ellipse(self.win, (250,250,250), [ix + x-r, iy + y-r, r*2,r*2])
        pygame.draw.ellipse(self.win, (0,0,0), [ix + x-r, iy + y-r, r*2,r*2], 1)

    def isOnFocus(self, mpos):
        [ix, iy, iw, ih] = [*self.imgView.getStart(), *self.imgView.getSize()]
        [mx, my] = mpos
        [x, y, r2, _] = self.pos
        r = r2/2
        x += ix
        y += iy
        if x-r < mx < x+r and y-r < my < y+r:
            return True
        return False
    
    def passMouseEvents(self, events):
        for e in events:
            if e.type == pygame.MOUSEBUTTONDOWN:
                return e.button
        return None

    def spawn(self, events, mpos, mpress):
        self.draw()

        if self.isOnFocus(mpos):
            b = self.passMouseEvents(events)
            if b == 1:
                self.pressed = True
        if not mpress[0]:
            self.pressed = False
        
        if self.pressed:
            [ix, iy, iw, ih] = [*self.imgView.getStart(), *self.imgView.getSize()]
            [mx, my] = mpos
            self.pos[0] = mx-ix
            self.pos[1] = my-iy

            if self.pos[0] < 0: self.pos[0] = 0
            if self.pos[1] < 0: self.pos[1] = 0
            if self.pos[0] > iw: self.pos[0] = iw
            if self.pos[1] > ih: self.pos[1] = ih

        ...


class ImageView(BaseView, MouseSensView):
    def __init__(self, win, file=None, img=None, coords="[0, 0]", isButton="False", resize="1.0", size=None, **kwargs):
        self.win:pygame.Surface = win
        self.coords = coords
        self.file = file
        self.resize = eval(resize)
        self.isButton = eval(isButton)
        if file != None or img != None:
            self.base_img = pygame.image.load(file) if img==None else img
            
            self.img = self.base_img.copy()

            [w, h] = self.base_img.get_size()
            if size == None:
                self.scaled_img = pygame.transform.scale(self.base_img, (w*self.resize, h*self.resize))
            else:
                size = eval(size)
                self.scaled_img = pygame.transform.scale(self.base_img, (size, size))
        
        self.angle = 0
        self.bg = None

        self.onclick = [lambda:..., ()]

        # направляющая
        self.dirLine = DirLine(self.win, self)
        # окружность
        self.circleLine = CircleLine(win, self)


    def update(self, img:pygame.Surface):
        self.base_img = img
        self.img = self.base_img.copy()
        [w, h] = self.base_img.get_size()
        self.scaled_img = pygame.transform.scale(self.base_img, (w*self.resize, h*self.resize))

    def getStart(self):
        return self.coords
    def getSize(self):
        return [self.scaled_img.get_width(), self.scaled_img.get_height()]
    
    def isOnFocus(self, mpos):
        [mx, my] = mpos
        [x, y, w, h] = [*self.coords, *self.getSize()]
        if x < mx < x+w and y < my < y+h:
            return True
        return False
    
    def default(self):
        self.base_img = pygame.image.load(self.file)
        self.img = self.base_img.copy()

        [w, h] = self.base_img.get_size()
        self.scaled_img = pygame.transform.scale(self.base_img, (w*self.resize, h*self.resize))
        
    
    def rotate(self, a):
        self.angle = a
        # перевод из pygame.Surface в PIL.Image.Image
        [w, h] = self.base_img.get_size()
        pixel_data = pygame.image.tostring(self.base_img, 'RGBA')
        im = Image.frombytes('RGBA', (w, h), pixel_data)
        im = im.rotate(a)

        # перевод обратно в pygame.Surface
        pixel_data = im.tobytes()
        self.img = pygame.image.fromstring(pixel_data, [w, h], 'RGBA')
        [w, h] = self.base_img.get_size()
        self.scaled_img = pygame.transform.scale(self.img, (w*self.resize, h*self.resize))


    def cut(self):
        def dist(x1,y1, x2,y2):
            return ((x1-x2)**2 + (y1-y2)**2)**0.5
        
        [rx, ry] = self.circleLine.pos[:2:]
        rx /= self.resize
        ry /= self.resize
        radius = self.circleLine.radius
        # перерасчет координат rx, ry
        [w, h] = self.base_img.get_size()
        [crx, cry] = [w//2, h//2]
        dx = rx - crx
        dy = ry - cry

        angle_rad = math.radians(self.angle)
        rx = crx + dx * math.cos(angle_rad) - dy * math.sin(angle_rad)
        ry = cry + dx * math.sin(angle_rad) + dy * math.cos(angle_rad)

        # перевод из pygame.Surface в PIL.Image.Image
        pixel_data = pygame.image.tostring(self.base_img, 'RGBA')
        im = Image.frombytes('RGBA', (w, h), pixel_data)
        pix = im.load()
        # print([rx, ry], radius)
        for r in range(im.height):
            for c in range(im.width):
                if dist(c,r, rx,ry) > radius:
                    pix[c, r] = (0,0,0,0)
                    
        
        # перевод обратно в pygame.Surface
        pixel_data = im.tobytes()
        self.base_img = pygame.image.fromstring(pixel_data, [w, h], 'RGBA')
        # self.img = pygame.image.fromstring(pixel_data, [w, h], 'RGBA')


        [w, h] = self.base_img.get_size()
        # print((w, h), (w*self.resize, h*self.resize))
        self.scaled_img = pygame.transform.scale(self.base_img, (w*self.resize, h*self.resize))
        # print(self.angle)
        self.rotate(self.angle)


    def spawn(self, events, mpos, mpress, **_) -> bool:

        if self.isButton:
            [x, y, w, h] = [*self.coords, *self.getSize()]

            if self.isOnFocus(mpos):
                pygame.draw.rect(self.win, (100,150,255), [x, y, w, h])
                button = self.passMouseEvents(events)
                if button == 1:
                    self.onclick[0](*self.onclick[1])
            
            if self.bg:
                pygame.draw.rect(self.win, self.bg, [x, y, w, h])

        self.win.blit(self.scaled_img, self.coords)

        if self.isButton and self.bg:
            self.circleLine.spawn(events, mpos, mpress)
            self.dirLine.spawn(events, mpos, mpress)

        return False    