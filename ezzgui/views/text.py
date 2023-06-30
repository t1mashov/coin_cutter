
import pygame

class Text:
    def __init__(self, text='', font='Arial', size=18, color=(0,0,0)):
        self.color = color
        self.text = text
        self.font = pygame.font.SysFont(font, size)
        self.picture = self.font.render(text, True, self.color) if text!='' else None
    def render(self):
        self.picture = self.font.render(self.text, True, self.color)
    
