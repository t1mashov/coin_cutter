
import pygame

class View:
    def __init__(self, win, pos, on_click_func=None):
        self.win = win
        self.pos = pos
        self.on_click_func = on_click_func

    def on_focus(self, mpos):
        [mx, my] = mpos
        [x, y, w, h] = self.pos
        if x < mx < x+w and y < my < y+h:
            return True
        return False
    
    def on_click_detect(self, events, mpos):
        if self.on_click_func == None: return
        if not self.on_focus(mpos): return
        for e in events:
            if e.type == pygame.MOUSEBUTTONDOWN:
                if e.button == 1:
                    self.on_click_func[0]( *self.on_click_func[1])



class MouseSensView:
    '''Объекты, чувствительные к мыши'''
    def __init__(self, win, pos):
        self.win = win
        self.pos = pos

    def isOnFocus(self, mpos):
        [mx, my] = mpos
        [x, y, w, h] = self.pos
        if x < mx < x+w and y < my < y+h:
            return True
        return False
    
    def passMouseEvents(self, events):
        for e in events:
            if e.type == pygame.MOUSEBUTTONDOWN:
                return e.button
        return None
            

