
import pygame

from ezzgui.views.base_view import BaseView
from ezzgui.views.view import MouseSensView 



class SeekBar(BaseView, MouseSensView):
    def __init__(self, win, pos, 
                 thumbColor="[80]*3", bgColor="[150]*3", markedColor="[150]*3",
                 points="list(range(10))", cursor=0,
                 onChange=[lambda:..., ()], **kwrags):
        self.win = win
        self.pos = pos
        self.thumbColor = eval(thumbColor)
        self.bgColor = eval(bgColor)
        self.markedColor = eval(markedColor)
        self.points = eval(points)
        self.onChange = onChange
        self.cursor = eval(cursor)

        # print(self.points)

        self.tw = 8
        self.pressed = False

    def getStart(self):
        return self.pos[:2:]
    def getSize(self):
        return self.pos[2::]
    
    def getValue(self):
        return self.points[self.cursor]
    
    def draw(self):
        [x, y, w, h] = self.pos
        lh = 8
        tw = self.tw
        ly = y + h//2 - lh//2
        pln = len(self.points) - 1
        dw = w / pln
        # dw = w // pln
        # print(dw, pln, w, w/19, w/20)
        cur = self.cursor

        pygame.draw.rect(self.win, self.bgColor, [x+lh//2,ly, w-lh//2,lh])
        pygame.draw.ellipse(self.win, self.bgColor, [x+w-lh//2,ly,lh,lh])
        pygame.draw.rect(self.win, self.markedColor, [x+lh//2,ly, cur*dw,lh])
        pygame.draw.ellipse(self.win, self.markedColor, [x,ly,lh,lh])

        pygame.draw.ellipse(self.win, self.thumbColor, [x + dw*cur, y, tw, tw])
        pygame.draw.ellipse(self.win, self.thumbColor, [x + dw*cur, y+h-tw, tw, tw])
        pygame.draw.rect(self.win, self.thumbColor, [x + dw*cur, y+tw//2, tw, h-tw])
        ...


    def detect_move(self, events, mpos, mpress):
        button = self.passMouseEvents(events)
        if self.isOnFocus(mpos) and button == 1:
            self.pressed = True
        if not mpress[0]:
            self.pressed = False
        if self.pressed:
            [x, y, w, h] = self.pos
            [mx, my] = mpos
            tw = self.tw
            pln = len(self.points) - 1
            dw = w / pln
            new_c = round((mx - tw//2 - x) / dw)
            if new_c > pln:
                new_c = pln
            if new_c < 0:
                new_c = 0
            if new_c != self.cursor:
                self.cursor = new_c
                self.onChange[0](*self.onChange[1])

    
    def spawn(self, events, mpos, mpress, keys, **kwargs) -> bool:

        self.draw()
        self.detect_move(events, mpos, mpress)

        return False