
import pygame

from .base_view import BaseView

''' xml:
<rect
    id="rct"
    pos="[10,10,250,100]"
    color="(255,0,0)"
    stroke="3"
    />
'''
class Rect(BaseView):
    def __init__(self, win, pos, color='(0,0,0)', stroke='-1', **kwargs):
        self.win = win
        self.pos = pos
        self.color = eval(color)
        self.stroke = eval(stroke)

    def getSize(self):
        return self.pos[2::]
    def getStart(self):
        return self.pos[:2:]

    def spawn(self, **kwargs):
        if self.stroke == -1:
            pygame.draw.rect(self.win, self.color, self.pos)
        else:
            pygame.draw.rect(self.win, self.color, self.pos, self.stroke)


''' xml:
<ellipse
    id="e1"
    pos="[10,10,250,100]"
    color="(255,0,0)"
    stroke="3"
    />
'''
class Ellipse(BaseView):
    def __init__(self, win, pos, color='(0,0,0)', stroke='-1', **kwargs):
        self.win = win
        self.pos = pos
        self.color = eval(color)
        self.stroke = eval(stroke)

    def getSize(self):
        return self.pos[2::]
    def getStart(self):
        return self.pos[:2:]

    def spawn(self, **kwargs):
        if self.stroke == -1:
            pygame.draw.ellipse(self.win, self.color, self.pos)
        else:
            pygame.draw.ellipse(self.win, self.color, self.pos, self.stroke)