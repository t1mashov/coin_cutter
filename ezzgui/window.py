
import pygame
pygame.init()
import sys

from .imports import *


class Window:
    def __init__(self, design={}, size=(800, 500), bg=[255]*3, win=None, name=''):
        self.design = design
        self.size = size
        self.bg = bg
        if win == None:
            self.win = pygame.display.set_mode(self.size)
            pygame.display.set_caption(name)
        else:
            self.win = win
        ...
    
    def run(self):
        '''Запуск главного цикла приложения'''
        clock = pygame.time.Clock()
        while True:
            clock.tick(60)
            self.win.fill(self.bg)

            events = pygame.event.get()
            mpos = pygame.mouse.get_pos()
            mpress = pygame.mouse.get_pressed()
            keys = pygame.key.get_pressed()

            for e in events:
                if e.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

            for view in self.design.values():
                view.spawn(**{
                    'events' : events,
                    'mpos' : mpos,
                    'mpress' : mpress,
                    'keys' : keys,
                })

            pygame.display.update()
            
