
import pygame
from .ids import next
from .text import Text
from .view import View
from .base_view import BaseView

''' xml: 
<button 
    coords="(10,10)"
    text="Click me!"
    font="Arial" 
    padding="[5, 2]"
    bgColor="[150]*3"
    hoverColor="[210]*3"
    /> 
'''
class Button(View, BaseView):
    def __init__(self, win, coords, 
                 text='', font='Arial', size='18', padding='[5, 0]', 
                 on_click_func=None, tag=None,
                 textColor="(0,0,0)",
                 bgColor='(150,150,150)', hoverColor='(200,200,200)', **kwargs):
        self.on_click_func = on_click_func
        self.default_bg_color = eval(bgColor)
        self.on_focus_bg_color = eval(hoverColor)
        self.text = Text(text, font=font, size=eval(size), color=eval(textColor))
        self.tag = tag
        [w, h] = self.text.font.size(text)
        self.pd = eval(padding)
        self.pos = [*coords, w+self.pd[0]*2, h+self.pd[1]*2]
        super().__init__(win, self.pos, self.on_click_func)

    def getSize(self):
        return self.pos[2::]
    def getStart(self):
        return self.pos[:2:]
    
    def spawn(self, events, mpos, **kwargs):
        self.on_click_detect(events, mpos)
        if self.on_focus(mpos):
            pygame.draw.rect(self.win, self.on_focus_bg_color, self.pos)
        else:
            pygame.draw.rect(self.win, self.default_bg_color, self.pos)
        [x, y, _, _] = self.pos
        self.win.blit(self.text.picture, (x+self.pd[0], y+self.pd[1]))