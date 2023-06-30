
import pygame

from ezzgui.views.button import Button
from ezzgui.views.text_view import TextView
from ezzgui.views.table import Table
from ezzgui.views.view import MouseSensView

from .views.base_view import BaseView

class ScrollView(MouseSensView, BaseView):
    def __init__(self, win, pos, bg='[255]*3', speed="10", invert="False", **kwargs):
        self.elements:dict = {}
        self.win = win
        self.pos = pos
        self.invert = eval(invert)
        self.speed = eval(speed)
        self.bg = eval(bg)
        self.surf = pygame.Surface(pos[2::])
        self.surf.fill(self.bg)

        self.shift = False
        self.dx = 0
        self.dy = 0

        self.max_xy = [0, 0]


    def set_elements(self, elements):
        self.dx = 0
        self.dy = 0
        self.elements = elements
        for item in self.elements.values():
            item.win = self.surf
        self.max_xy = self.calc_maxes()

    
    def get_surface(self):
        return self.surf

    
    def calc_maxes(self):
        max_xy = [0, 0]
        for item in self.elements.values():
            ix, iy, iw, ih = [*item.getStart(), *item.getSize()]
            if ix+iw > max_xy[0]:
                max_xy[0] = ix+iw
            if iy+ih > max_xy[1]:
                max_xy[1] = iy+ih
        return max_xy


    def detect_keydown(self, keys):
        if keys[pygame.K_LSHIFT]:
            self.shift = True
        else:
            self.shift = False


    def getSize(self):
        return self.pos[2::]
    def getStart(self):
        return self.pos[:2:]
    
    def isElVisible(self, element):
        ex, ey = element.getStart()
        ew, eh = element.getSize()
        x, y = self.getStart()
        w, h = self.getSize()
        
        if (ex + ew < 0) or (w < ex) or (ey + eh < 0) or (h < ey):
            return False
        return True


    
    def spawn(self, events, mpos, mpress, keys, **kwargs):
        self.surf.fill(self.bg)

        # print(self.dx, self.dy)

        X, Y = self.getStart()
        W, H = self.getSize()
        vis = 0
        mouseCatchedByChild = False
        for item in self.elements.values():
            if self.isElVisible(item):
                vis += 1
                [mx, my] = mpos
                mouseCatchedByElement = item.spawn(events=events, mpos=[mx-X, my-Y], mpress=mpress, keys=keys)
                if mouseCatchedByElement:
                    mouseCatchedByChild = True

        # print(mouseCatchedByChild)
        
        self.win.blit(self.surf, self.pos[:2:])

        self.detect_keydown(keys)

        if self.isOnFocus(mpos) and mouseCatchedByChild in (None, False):
            click = self.passMouseEvents(events)
            d = [0, 0]
            if click == 4:
                if self.invert:
                    if self.shift: d[1] += self.speed
                    else:  d[0] += self.speed
                else:
                    if self.shift: d[0] += self.speed
                    else:  d[1] += self.speed
            elif click == 5:
                if self.invert:
                    if self.shift: d[1] -= self.speed
                    else: d[0] -= self.speed
                else:
                    if self.shift: d[0] -= self.speed
                    else: d[1] -= self.speed

            if click != None:
                self.move(d)
            
            

    def move(self, d):
        W, H = self.getSize()
        self.dx += d[0]
        self.dy += d[1]

        mmx, mmy = self.max_xy
        if self.dx > 0:
            self.dx = 0
            d[0] = 0
        if self.dx + mmx < W:
            d[0] = 0
            self.dx = W - mmx
        if self.dy > 0:
            d[1] = 0
            self.dy = 0
        if self.dy + mmy < H:
            d[1] = 0
            # d[1] = H - mmy - (self.dy - d[1])
            self.dy = H - mmy

        
        for item in self.elements.values():
            try:
                item.pos[0] += d[0]
                item.pos[1] += d[1]
            except:
                ix, iy = item.coords
                item.coords = (ix+d[0], iy+d[1])


                