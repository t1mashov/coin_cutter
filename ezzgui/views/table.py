
import pygame

from .text import Text
from .view import MouseSensView
import copy
from .base_view import BaseView

'''
<table
    pos="[10,10,150,100]"
    bg="(255,255,255)"
    padding="[5,2]"
    size="14"
    />
'''
class Table(MouseSensView, BaseView):
    def __init__(self, win, pos, bg='(255,255,255)', padding='[5, 2]', 
                 scrollCatcher = "False",
                 color="(0,0,0)", font="", size="16", **kwargs):
        super().__init__(win, pos)
        self.win = win
        self.pos = pos
        self.color = eval(color)
        self.bg = eval(bg)
        self.padding = eval(padding)
        self.scrollCatcher = scrollCatcher

        self.content = {} # {1 : {'id':1, 'prod':'Утюг'}, ...}
        self.headers = {} # {'id':'ID', 'prod':"Product", ...}
        self.widths = {} # {ключ столбца : наибольшая длина отрендеренного текста в столбце}

        self.render_table = {}
        self.size = []

        self.dx = 0
        self.dy = 0
        self.old_d = [self.dx, self.dy]
        self.speed = 10
        self.shift = False # зажата ли клавиша SHIFT

        # поверхность отрисовки
        self.surf = pygame.Surface(pos[2::])
        self.surf.fill(self.bg)
        self.text = Text(font=font, size=eval(size), color=self.color)

        self.rowID = 1 # авто-индекс строк
        self.rowHeight = self.text.font.size(' ')[1] + self.padding[0]

    def getSize(self):
        return self.pos[2::]
    def getStart(self):
        return self.pos[:2:]

    def next_id(self):
        return self.rowID
    
    def detect_keydown(self, keys):
        if keys[pygame.K_LSHIFT]:
            self.shift = True
        else:
            self.shift = False

    # устанавливает стандартные headers если они не были заданы
    def check_default_header(self):
        if len(self.content.keys()) == 0: return
        rk = list(self.content.keys())[0]
        if len(self.headers) == 0:
            self.headers = {k:k for k in self.content[rk].keys()}
        

    # row == {'id':3, 'name':'Alex', ...}
    def add_row(self, row:dict):
        self.content[str(self.rowID)] = row
        self.check_default_header()
        self.rowID += 1
        self.update_render_table()

    
    def set_data(self, data):
        self.content = data
        self.rowID = max([int(k) for k in data.keys()])+1
        self.update_render_table()

    def add_rows(self, rows:dict):
        for row in rows:
            self.add_row(row)
        

    # функция:
    # -- ререндер таблицы
    # -- перерасчет widths
    # -- перерасчет size
    def update_render_table(self):
        self.check_default_header()
        self.render_table = {}
        self.render_table['header'] = {}
        for (k, v) in self.headers.items():
            self.text.text = f'{v}'
            self.text.render()
            self.render_table['header'][k] = self.text.picture

            for (i, row) in self.content.items():
                
                if not i in self.render_table.keys(): # чтоб строки не затирались
                    self.render_table[i] = {}
                
                if not k in row.keys(): row[k] = '' # если значение ячейки не задано

                self.text.text = f'{row[k]}'
                self.text.render()
                self.render_table[i][k] = self.text.picture

        
        # обновление width
        self.widths = {
            k : max(
                [row[k].get_rect().size[0] for row in self.render_table.values()]
            )
            for k in self.headers.keys()
        }

        self.size = [
            sum(self.widths.values()) + self.padding[0]*2 * len(self.headers),
            (self.rowHeight + self.padding[1]*2) * (len(self.content) + 1)
        ]
        self.render()



    # рендерит таблицу на self.surf (с сеткой)
    def render(self):
        self.surf.fill(self.bg)
        [dx, dy] = [self.dx, self.dy]
        ox = 0 # X-координата линии
        [W, H] = self.size

        padX, padY = self.padding
        for k in self.headers.keys():
            
            [self.surf.blit(row[k], (dx + ox+padX, dy + i * (self.rowHeight + padY*2) + padY*2)) 
             for (i, (_, row)) in enumerate(self.render_table.items())]
            
            pygame.draw.rect(self.surf, self.color, # вертикальные линии
                [dx + ox, dy, 1, H]
            )

            ox += self.widths[k] + padX*2

        for i in range(len(self.content)+1):
            pygame.draw.rect(self.surf, self.color, # горизонтальные линии
                [dx, dy + i*(self.rowHeight + padY*2), W, 1]
            )

        pygame.draw.rect(self.surf, self.color, [dx, dy, W, H], 1) # рамка
        


    # header == {'id':'ID', 'prod':"Product", ...}
    def set_header(self, header:dict):
        self.headers = header
        self.update_render_table()

    
    def spawn(self, events, mpos, keys, **kwargs):
        self.win.blit(self.surf, self.pos[:2:])

        if self.size == []: return # чтоб не вылетало если таблица не заполнена

        self.detect_keydown(keys)

        mouseCatched = False

        if self.isOnFocus(mpos):
            click = self.passMouseEvents(events)
            if click == 4:
                if self.shift:
                    self.dx += self.speed
                else: self.dy += self.speed
            elif click == 5:
                if self.shift:
                    self.dx -= self.speed
                else: self.dy -= self.speed
            
            mouseCatched = True

            if click != None:

                [w, h] = self.size
                [tw, th] = self.pos[2::]

                if self.dx+w < tw: self.dx = tw-w
                if self.dy+h < th:  self.dy = th-h
                if self.dx > 0:  self.dx = 0
                if self.dy > 0:  self.dy = 0

                if self.old_d == [self.dx, self.dy]:
                    mouseCatched = False

                if self.scrollCatcher:
                    mouseCatched = True

                self.old_d = [self.dx, self.dy]

                self.render()

        return mouseCatched