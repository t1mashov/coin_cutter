
'''
# Использование
# (textarea 1.2.3)

import textarea

...

# init
area = textarea.TextArea(win, [10, 10, 165, 100])

# Фон цветом
area.bg.set_color((200,200,200))

# Фон функцией
def draw_bg(): pygame.draw.ellipse(...)

area.bg.set_func(draw_bg, ())

# Настройки текста
# (использовать шрифты только с одинаковой шириной символов)
area.text.set_settings(
    font_name='Courier',
    font_size=14
)

# Настройки курсора
area.cursor.set_settings(
    color=(100,50,50)
)

# Цвет фона выделенного текста
area.selection.color = (200,200,255)

# Функция на событие on_disable (on_enable)
def foo(x, y):
    print x+y
area.on_disable = [foo, (x, y)]

# Функция на событие изменения текста
area.on_text_change = [foo, (x, y)]

# Содержимое
area.set_content("Hello everyone!!!\nIt's texteditor for pygame apps")

...

events = pygame.event.get()

mpos = pygame.mouse.get_pos()

mpress = pygame.mouse.get_pressed()

keys = pygame.key.get_pressed()

...

area.spawn(events, mpos, mpress, keys)

...

pygame.display.update()

'''


import pygame
import pyperclip
from .base_view import BaseView

class TextArea(BaseView):
    class BG:
        def __init__(self, win, pos):
            self.pos = pos
            self.win = win
            self.func = None
            self.params = None
            self.color = None
        def set_func(self, func, params):
            self.func = func
            self.params = params
        def set_color(self, color):
            self.color = color
        def draw(self):
            if self.color != None:
                pygame.draw.rect(self.win, self.color, self.pos)
            if self.func != None:
                self.func(*self.params)

    class TEXT:
        def __init__(self, win, pos, ta):
            self.win = win
            self.pos = pos
            self.ta = ta
            self.color = (0,0,0)
            self.font = pygame.font.SysFont('lucida console', 18)
        def set_settings(self, font_name='lucida console', font_size=18, color=(0,0,0)):
            self.font = pygame.font.SysFont(font_name, font_size)
            self.color = color
            self.ta.updated_text_settings()
        def render(self, text:str, smooth=True):
            return self.font.render(text, smooth, self.color)
        def get_area_size(self):
            [w, h] = self.font.size(' ')
            return [self.pos[2]//w, self.pos[3]//h]
        def char_size(self):
            return self.font.size(' ')

    class CURSOR:
        def __init__(self, win, pos, ta):
            self.win = win
            self.pos = pos
            self.ta:TextArea = ta

            self.x = 0
            self.y = 0
            self.active = False
            self.ct = 0
            self.c_size = self.ta.text.char_size()
            self.color = (0, 0, 0)
        def spawn(self):
            if self.active and self.is_visible():
                self.ct = (self.ct + 1) % 50
                [csw, csh] = self.c_size
                [ox, oy] = self.ta.offset
                # pos = self.pos
                pos = self.ta.pos
                if self.ct < 30:
                    pygame.draw.rect(self.win, self.color, 
                        [
                            self.x*csw + pos[0] - ox*csw + self.ta.d, 
                            self.y*csh + pos[1] - oy*csh + self.ta.d, 
                            2, csh]
                    )
        def set_coords(self, x=None, y=None):
            if x != None: self.x = x
            if y != None: self.y = y

        # проверяет, не вышел ди курсор за пределы textaera_size и исправляет, если так
        def correct_coords(self):
            [w, h] = self.ta.text_area_size
            if self.x > w: self.x = w
            if self.x < 0: self.x = 0
            if self.y > h: self.y = h
            if self.y < 0: self.y = 0
            if self.y > h-1: # клик ниже текста
                self.y = h-1
            if self.x > len(self.ta.lines[int(self.y)]):
                self.x = len(self.ta.lines[int(self.y)]) # перенос курсора в конец строки если он дальше
        
        # проверка, находится ли курсор в области видимости
        def is_visible(self):
            [ox, oy] = self.ta.offset
            [cx, cy] = [self.x, self.y]
            [w, h] = self.ta.table
            if ox <= cx <= ox+w and oy <= cy < oy+h:
                return True
            return False
        
        # сдвигает offset, чтобы cursor был в поле зрения
        # вызывать при нажатии на кнопки
        def keep_visible(self):
            [ox, oy] = self.ta.offset
            [w, h] = self.ta.table
            [mw, mh] = self.ta.text_area_size
            
            if self.x >= ox+w or self.x <= ox:
                if mw - self.x < w//2:
                    ox = mw - w
                elif self.x < w//2:
                    ox = 0
                else:
                    ox = self.x - w//2

            if self.y<oy: 
                oy = self.y
            elif self.y>oy+h-1:
                oy = self.y-h+1
            
            if ox + w > mw: ox = mw - w
            if oy + h > mh: oy = mh - h
            if ox < 0: ox = 0
            if oy < 0: oy = 0

            self.ta.offset[0] = ox
            self.ta.offset[1] = oy
            self.ta.render()

        def move(self, dx, dy, keyboard=False):
            self.y = int(self.y)
            self.x = int(self.x)
            if self.x == 0 and dx == -1 and self.y > 0:
                self.y -= 1
                self.x = len(self.ta.lines[self.y])
            elif self.x == len(self.ta.lines[self.y]) and dx == 1 and self.y < self.ta.text_area_size[1]-1:
                self.y += 1
                self.x = 0
            else:
                self.x += dx
                self.y += dy
            if keyboard:
                self.keep_visible()
                self.correct_coords()

        def enable(self):
            self.active = True
        def disable(self):
            self.active = False

        def set_settings(self, color=(0,0,0)):
            self.color = color
        
        def set_from_mouse_pos(self, mpos):
            [x, y] = mpos
            [ox, oy] = self.ta.offset
            # x -= self.pos[0]
            # y -= self.pos[1]
            x -= self.ta.pos[0]
            y -= self.ta.pos[1]
            self.x = round(x/self.c_size[0]) + ox
            self.y = y//self.c_size[1] + oy
            self.correct_coords()
            self.ct = 0

    class SELECTION:
        def __init__(self, win, ta, color=(190,190,250)):
            self.win = win
            self.ta:TextArea = ta
            self.cursor:TextArea.CURSOR = ta.cursor
            self.color = color
            self.poses = [(0,0), (0,0)]
            self.cs = self.ta.text.char_size()
            self.lines = []
            self.s_rows = {}
            self.fst_click = True # для удаления "мерцания" при переносе курсора

        def is_selected(self):
            return not self.poses[0] == self.poses[1]

        def get_cursor_pos_from_mouse(self, mpos):
            [mx, my] = mpos
            [ox, oy] = self.ta.offset
            [w, h] = self.ta.text_area_size
            # mx -= self.cursor.pos[0]
            # my -= self.cursor.pos[1]
            mx -= self.ta.pos[0]
            my -= self.ta.pos[1]
            mcx = round(mx/self.cs[0]) + ox
            mcy = my//self.cs[1] + oy
            if mcx < 0: mcx = 0
            if mcx > w: mcx = w
            if mcy < 0: mcy = 0
            if mcy > h: mcy = h
            
            if mcy > h-1:
                mcy = h-1
            if mcx > len(self.ta.lines[int(mcy)]):
                mcx = len(self.ta.lines[int(mcy)])
            return (mcx, mcy)


        def detect(self, mpos, press, events):
            if self.ta.detect_focus(mpos, events):
                if press[0]:
                    self.cursor.correct_coords()
                    # удаление "мерцания" при переносе курсора
                    if self.fst_click: 
                        self.fst_click = False
                        self.poses = [(0, 0), (0, 0)]
                        return
                        
                    self.poses = [
                        (self.cursor.x, self.cursor.y),
                        self.get_cursor_pos_from_mouse(mpos)
                    ]
                    self.s_rows = self.selected_rows()
                    
                    #print('<SELECTION.detect>', self.poses)
                else:
                    self.fst_click = True

        def abs_pos(self, cpos):
            [x, y] = cpos
            # dpos = self.ta.text.pos
            dpos = self.ta.pos
            cs = self.cursor.c_size
            return [
                (x)*cs[0] + dpos[0],
                (y)*cs[1] + dpos[1]
            ]

        # возвращает {line_idx : [start, stop], ...}
        # если copy=True, собирает в self.lines выделенный текст 
        def selected_rows(self):
            [start, end] = sorted(self.poses, key=lambda el:el[1])
            # [start, end] = sorted(self.ta.pos, key=lambda el:el[1])
            if start[1] == end[1]:
                [start, end] = sorted([start, end], key=lambda el:el[0])
                return {start[1] : [start[0], end[0]]}
            else:
                start_line = self.ta.lines[start[1]]
                res = {}
                res[start[1]] = [start[0], len(start_line)]
                for y in range(start[1]+1, end[1]):
                    line = self.ta.lines[y]
                    res[y] = [0, len(line)]
                res[end[1]] = [0, end[0]]
                return res

        # возвращает видимую часть res=selected_rows()
        def get_visible_ranges(self):
            dct = self.s_rows
            [ox, oy] = self.ta.offset
            [w, h] = self.ta.table
            res = {}
            for y, [s, e] in dct.items():
                if oy <= y < oy+h:
                    s -= ox
                    e -= ox
                    if s < 0: s = 0
                    if e < 0: continue
                    if e > w: e = w
                    res[y-oy] = [s, e]
            return res

        # отображение выделения
        def draw(self):
            rngs = self.get_visible_ranges()
            if rngs == {}: return
            if self.poses[0] == self.poses[1]: return
            cs = self.cs
            rectes = []
            for y, [s, e] in rngs.items():
                [x1, y1] = self.abs_pos([s, y])
                [x2, _] = self.abs_pos([e, y])
                rectes.append([x1 + self.ta.d, y1 + self.ta.d, x2-x1+cs[0], cs[1]])
            for rct in rectes:
                pygame.draw.rect(self.win, self.color, rct)
        

        def detect_keydown(self, events):
            def delete_selection():
                if len(self.s_rows) == 1:
                    spx = sorted(self.poses, key=lambda el:el[0])
                    self.cursor.set_coords(*spx[0])
                    y = spx[0][1]
                    line = self.ta.lines[y]
                    self.ta.lines[y] = line[:spx[0][0]:] +line[spx[1][0]+1::]
                    ...
                else:
                    spy = sorted(self.poses, key=lambda el:el[1])
                    self.cursor.set_coords(*spy[0])

                    eline = self.ta.lines[spy[1][1]][spy[1][0]+1::]

                    # вырезаем промежуточные полные строки
                    self.ta.lines = self.ta.lines[:spy[0][1]+1:] + self.ta.lines[spy[1][1]+1::]
                
                    self.ta.lines[spy[0][1]] = self.ta.lines[spy[0][1]][:spy[0][0]:] + eline
                    
            if self.is_selected():
                for e in events:
                    if e.type == pygame.KEYDOWN:

                        #print(e.unicode, e.key)

                        if e.key == 99 and self.ta.ctrl: # ctrl + c
                            text = '\n'.join([
                                self.ta.lines[y][s:e+1:]
                                for y, [s, e] in self.s_rows.items()
                            ])
                            pyperclip.copy(text)

                        elif e.key == 118 and self.ta.ctrl: # ctrl + v
                            delete_selection()
                            self.ta.paste_text(pyperclip.paste())
                            self.poses = [(0, 0), (0, 0)]
                            self.ta.render()
                        
                        elif not e.key in [pygame.K_LSHIFT, pygame.K_RSHIFT, pygame.K_LCTRL, pygame.K_RCTRL, 
                                           pygame.K_UP, pygame.K_DOWN, pygame.K_LEFT, pygame.K_RIGHT]:
                            
                            delete_selection()

                            [cx, cy] = [self.cursor.x, self.cursor.y]
                            try:
                                line = self.ta.lines[cy]
                            except: return

                            if e.key == 9: #tab
                                self.ta.lines[cy] = line[:cx:] + ' '*self.ta.tab_len + line[cx::]
                                self.cursor.move(4, 0, True)
                            elif e.key == 8: ...
                            elif e.unicode != '':
                                self.ta.lines[cy] = line[:cx:] + e.unicode + line[cx::]
                                self.cursor.move(1, 0, True)

                            self.ta.render()
                            self.poses = [(0, 0), (0, 0)]
                       
                        if e.key in [8, 9, 13, 118] or e.unicode != '':
                            if self.ta.on_text_change != None:
                                self.ta.on_text_change[0](*self.ta.on_text_change[1])

                        if e.key in [pygame.K_UP, pygame.K_DOWN, pygame.K_LEFT, pygame.K_RIGHT]:
                            self.s_rows.clear()


        def spawn(self, mpos, mpress, events):
            if not self.ta.noreduct:
                self.detect(mpos, mpress, events)
            self.draw()


    class SCROLL_BAR:
        def __init__(self, ta, width, color, bg):
            self.ta = ta
            self.width = width
            self.color = color
            self.bg = bg

        def spawn(self):
            [X, Y, W, H] = self.ta.pos
            x = X + W - self.width
            v_len = len(self.ta.visible_text) # кол-во видимых линий
            v_len = v_len if v_len>0 else 1
            lines_len = len(self.ta.lines) # кол-во всех линий
            height = H * (v_len / lines_len) # высота ползунка
            
            w = self.width
            br = self.ta.offset[1] # кол-во линий до видимых
            try:
                sdy = (H - height) / (lines_len - v_len) # смещение по Y
            except:
                sdy = 0
            sy = sdy * br + Y # финальная координата Y для ползунка
            

            pygame.draw.rect(self.ta.win, self.bg, [x, Y, w, H]) # bg
            pygame.draw.rect(self.ta.win, self.color, [x, sy, w, height]) # bg
            



    def __init__(self, win, pos:list, padding='3', font="Lucida Console",
                 color='(0,0,0)', bg='(255,255,255)', 
                 selectionColor='(200,200,255)', cursorColor='(0,0,0)',
                 size='18',
                 text='',
                 scrollBarWidth="0",
                 scrollBarColor="[0]*3",
                 scrollBarBg="[255]*3",
                 **kwargs):
        self.win = win
        self.pos = pos
        self.lines = ['']
        self.visible_text = []
        self.render_lines = []
        self.offset = [0, 0] # chars pos
        self.one_row = False # disable 'enter' button
        self.noreduct = False # can only scroll text

        self.scrollBar = TextArea.SCROLL_BAR(
            self, eval(scrollBarWidth), eval(scrollBarColor), eval(scrollBarBg)
        )

        self.text_area_size = [0, 0]

        self.bg = TextArea.BG(self.win, pos)
        
        self.d = eval(padding)
        self.tab_len = 4
        
        text_pos = [pos[0]+self.d, pos[1]+self.d, pos[2]-self.d*4 - eval(scrollBarWidth), pos[3]-self.d*4]

        self.text = TextArea.TEXT(self.win, text_pos, self)

        self.table = self.text.get_area_size()
        self.cursor = TextArea.CURSOR(self.win, text_pos, self)

        self.selection = TextArea.SELECTION(self.win, self)

        self.bg.set_color(eval(bg))
        self.text.set_settings(
            font_name=font,
            font_size=eval(size),
            color=eval(color)
        )
        self.selection.color = eval(selectionColor)
        self.cursor.color = eval(cursorColor)

        self.onfocus = False
        self.shift = False
        self.ctrl = False

        self.on_enable = None
        self.on_disable = None
        self.on_text_change = None

        self.set_content(text)

    def getSize(self):
        return self.pos[2::]
    def getStart(self):
        return self.pos[:2:]

    def get_visible_text(self):
        self.text_area_size = [
            max([len(el) for el in self.lines]),
            len(self.lines)
        ]
        self.visible_text = []
        dx, dy = self.offset
        w, h = self.table
        for line in self.lines[dy:dy+h:]:
            self.visible_text += [line[dx:dx+w+1:]]

    def get_text(self):
        return '\n'.join(self.lines)

    def set_content(self, text):
        self.lines = text.split('\n')
        self.update_text_area()
        self.render()

    def paste_text(self, text):
        text = text.replace('\0', '')
        text = text.replace('\r', '')
        mas = text.split('\n')
        [cx, cy] = [self.cursor.x, self.cursor.y]
        line = self.lines[cy]
        if len(mas) == 1:
            self.lines[cy] = line[:cx:] + mas[0] + line[cx::]
        else:
            start = line[:cx:] + mas[0]
            end = mas[-1] + line[cx::]
            self.lines = self.lines[:cy:] + [start] + mas[1:-1:] + [end] + self.lines[cy+1::]

    def detect_focus(self, pos, events, scroll=False):
        on_mouse_focus = False
        click = False
        for e in events:
            if e.type == pygame.MOUSEBUTTONDOWN:
                if e.button in [1, 3]: click = True
        if not self.onfocus:
            if (self.pos[0] < pos[0] < self.pos[0]+self.pos[2] and
                self.pos[1] < pos[1] < self.pos[1]+self.pos[3]):
                on_mouse_focus = True
                if click:
                    self.onfocus = True
                    if not self.noreduct or scroll:
                        self.cursor.enable()
                        if self.on_enable:
                            self.on_enable[0](*self.on_enable[1])
        else:
            if (pos[0] < self.pos[0] or pos[0] > self.pos[0]+self.pos[2] or
                pos[1] < self.pos[1] or pos[1] > self.pos[1]+self.pos[3]):
                if click:
                    self.onfocus = False
                    if not self.noreduct or scroll:
                        self.cursor.disable()
                        if self.on_disable:
                            self.on_disable[0](*self.on_disable[1])
            else:
                on_mouse_focus = True
        return on_mouse_focus
        
    def render(self):
        self.get_visible_text()
        self.render_lines = [
            self.text.render(line) for line in self.visible_text
        ]

    def draw_text(self):
        for i, text_img in enumerate(self.render_lines):
            self.win.blit(text_img, [self.pos[0]+self.d, self.pos[1]+self.d+i*self.text.char_size()[1]])

    def updated_text_settings(self):
        self.table = self.text.get_area_size()
        self.cursor.c_size = self.text.char_size()
        self.selection.cs = self.text.char_size()
    
    def update_text_area(self):
        self.text_area_size = [
            max([len(el) for el in self.lines]),
            len(self.lines)
        ]
        
    def move_offset(self, dir): #dir == 'letf'...
        if dir == 'left' and self.offset[0] > 0:
            self.offset[0] -= 1
            return True
        elif dir == 'right' and self.offset[0]+self.table[0] < self.text_area_size[0]:
            self.offset[0] += 1
            return True
        elif dir == 'up' and self.offset[1] > 0:
            self.offset[1] -= 1
            return True
        elif dir == 'down' and self.offset[1]+self.table[1] < self.text_area_size[1]:
            self.offset[1] += 1
            return True
        return False

    
    def scroll_detect(self, e, mpos, mpress, events):
        mouseMoved = False
        if e.type == pygame.MOUSEBUTTONDOWN and self.detect_focus(mpos, events, scroll=True):
            if e.button == 4 and self.shift:
                mouseMoved += self.move_offset('left')
            elif e.button == 5 and self.shift:
                mouseMoved += self.move_offset('right')
            elif e.button == 4:
                mouseMoved += self.move_offset('up')
            elif e.button == 5:
                mouseMoved += self.move_offset('down')
            if e.button in [4, 5]:
                self.render()
                return mouseMoved

    def spawn(self, events, mpos, mpress, keys, **kwargs):
        self.detect_focus(mpos, events)

        self.bg.draw()
        
        self.selection.spawn(mpos, mpress, events)
        self.draw_text()
        self.scrollBar.spawn()

        if keys[pygame.K_LSHIFT] or keys[pygame.K_RSHIFT]:
            self.shift = True
        else:
            self.shift = False
        if keys[pygame.K_LCTRL] or keys[pygame.K_RCTRL]:
            self.ctrl = True
        else:
            self.ctrl = False

        mouseCatched = False
       
        for e in events:
            if self.onfocus and not self.noreduct:
                if e.type == pygame.KEYDOWN:

                    if e.key == pygame.K_LEFT: self.cursor.move(-1, 0, True)
                    if e.key == pygame.K_RIGHT: self.cursor.move(1, 0, True)
                    if e.key == pygame.K_UP: self.cursor.move(0, -1, True)
                    if e.key == pygame.K_DOWN: self.cursor.move(0, 1, True)


                    # get current line and it's index
                    line = ''
                    cy = int(self.cursor.y)
                    cx = self.cursor.x
                    if 0 <= cy < len(self.lines):
                        line = self.lines[cy]
                    else:
                        continue

                    if e.key == pygame.K_LEFT and self.ctrl:
                        for i in range(cx)[::-1]:
                            if not line[i] in ' ()[]{}':
                                self.cursor.move(-1, 0, True)
                            else:
                                break

                    if e.key == pygame.K_RIGHT and self.ctrl:
                        for i in range(cx, len(line)):
                            if not line[i] in ' ()[]{}':
                                self.cursor.move(1, 0, True)
                            else:
                                break

                    if self.selection.is_selected():
                        break

                    if e.key == 8: #backspace
                        if cx == 0:
                            if 0 < cy < len(self.lines):
                                #print('<spawn backspace> new[x,y]=', [len(self.lines[cy-1]), cy-1])
                                self.cursor.set_coords(len(self.lines[cy-1]), cy-1)
                                self.lines[cy-1] += self.lines[cy]
                                del self.lines[cy]
                        else:
                            deleted = False # было ли удалено что-нибудь с нажатым ctrl
                            if self.ctrl:
                                for i in range(cx)[::-1]:
                                    if not line[i] in ' ()[]{}':
                                        line = line[:i:]+line[i+1::]
                                        self.lines[cy] = line
                                        if self.offset[0] > 0: self.offset[0] -= 1
                                        self.cursor.move(-1, 0, True)
                                        deleted = True
                                    else:
                                        break
                                    
                            if not deleted:
                                line = line[:cx-1:]+line[cx::]
                                self.lines[cy] = line
                                self.cursor.move(-1, 0, True)
                        self.render()

                    elif e.key == 118 and self.ctrl: # ctrl + v
                        self.paste_text(pyperclip.paste())
                        self.render()
                         
                    elif e.key == 13: # enter
                        if self.one_row:
                            self.cursor.disable()
                            self.onfocus = False
                            if self.on_disable:
                                self.on_disable[0](*self.on_disable[1])
                            break
                        new_line = line[cx::]
                        self.lines[cy] = line[:cx:]
                        self.lines.insert(cy+1, new_line)
                        self.cursor.move(-self.cursor.x, 1, True)
                        self.render()

                    elif e.key == 9: # tab
                        self.lines[cy] = line[:cx:] + ' '*self.tab_len + line[cx::]
                        self.cursor.move(4, 0, True)
                        self.render()
                        

                    elif e.unicode != '':
                        self.lines[cy] = line[:cx:] + e.unicode + line[cx::]
                        self.cursor.move(1, 0, True)
                        self.render()
                        
                    if not e.key in [pygame.K_LSHIFT, pygame.K_RSHIFT]:
                        self.cursor.keep_visible()

                    if e.key in [8, 9, 13, 118] or e.unicode != '':
                        if self.on_text_change != None:
                            self.on_text_change[0](*self.on_text_change[1])


                if e.type == pygame.MOUSEBUTTONDOWN and self.detect_focus(mpos, events):
                    if e.button == 1:
                        self.cursor.set_from_mouse_pos(mpos)
                        v_line = ''
                        if 0 <= self.cursor.y < len(self.lines):
                            v_line = self.lines[int(self.cursor.y)]
                        if self.cursor.x > len(v_line):
                            self.cursor.x = len(v_line)
                        
                        self.cursor.keep_visible()
            
            if self.scroll_detect(e, mpos, mpress, events):
                mouseCatched = True
            
            
        if self.onfocus:
            self.cursor.spawn()

        if self.onfocus and not self.noreduct: 
            self.selection.detect_keydown(events)
        
        return mouseCatched
