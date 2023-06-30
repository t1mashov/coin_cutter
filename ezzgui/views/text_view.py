
import pygame
from .text import Text
from .base_view import BaseView

class TextView(BaseView):
    def __init__(self, win, coords, text='', font='Arial', size='18', color='(0,0,0)', **kwargs):
        self.win = win
        self.coords = coords
        self.content = text
        self.font = font
        self.size = eval(size)
        self.color = eval(color)
        self.text = Text(self.content, self.font, self.size, self.color)
        self.text.render()

    def set_text(self, txt):
        self.text.text = txt
        self.text.render()

    def getSize(self):
        return self.text.picture.get_rect().size
    def getStart(self):
        return self.coords

    def spawn(self, **kwargs):
        self.win.blit(self.text.picture, self.coords)