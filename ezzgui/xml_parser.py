
import xml.etree.ElementTree as ET
from xml.etree.ElementTree import Element

from .imports import *
from .scroll import ScrollView

'''
Контейнеры:

1) offset - смещение дочерних на dx и dy
<offset 
    dx="5" dy="5">
    ...
</offset>

2) vector - отображение элементов друг за другом c отступом margin (dir = вертикально[v]/горизонтально[h])
<vector 
    x="10" y="5" 
    dir="h" 
    margin="10">
    ...
</vector>

3) frozen - все объекты, помещенные в frozen не имеют размера с точки зрения <vector>,
следовательно помещаются "на задний фон"
<frozen>
    ...
</frozen> 

'''

class Parser:
    def __init__(self, str_xml):
        self.str_xml = str_xml
        self.XML_VIEWS = {}
        self.elements = {}
        self.defattrs = {}

        self.tag_views = {
            'rect' : Rect,
            'ellipse' : Ellipse,
            'text' : TextView,
            'input' : TextArea,
            'table' : Table,
            'button' : Button,
            'ScrollView' : ScrollView
        }

    def parse_element(self, win, el:Element, dx=0, dy=0):

        ID = el.attrib.get('id', next())
        
        attrs = el.attrib.copy()
        if 'coords' in el.attrib.keys():
            pos = eval(attrs.get('coords', '-1'))
        else:
            pos = eval(attrs.get('pos', '-1'))
        
        if pos == -1: pos = [dx, dy]
        else:
            x, y, *wh = pos
            pos = [x+dx, y+dy, *wh]

        pos = [int(el) for el in pos]
        
        attrs['pos'] = pos
        attrs['coords'] = pos

        attrs['win'] = win.win

        # default values
        for (k, v) in self.defattrs.items():
            if not k in attrs.keys():
                attrs[k] = v

        if el.tag in self.tag_views.keys():
            self.elements[ID] = self.tag_views[el.tag](**attrs)
        else:
            self.elements[ID] = self.XML_VIEWS[el.tag](**attrs)
        return ID


    # <offset>...</offset>
    def parse_offset(self, win, xml:Element, dx=0, dy=0):
        x = eval(xml.attrib.get('x', '0')) + dx
        y = eval(xml.attrib.get('y', '0')) + dy
        for el in xml:
            if el.tag == 'vector': 
                self.parse_vector(win, el, x, y)
            elif el.tag == 'offset':
                self.parse_offset(win, el, x, y)
            elif el.tag == 'default':
                self.defattrs = el.attrib
            elif el.tag == 'win':
                bg = eval(el.attrib.get('bg', '[230]*3'))
                win.bg = bg
            elif el.tag == 'frozen':
                self.parse_frozen(win, el, x, y)
            else:
                self.parse_element(win, el, x, y)
        return [x, y]


    # <vector dir="h">...</vector>
    def parse_vector(self, win, xml:Element, dx=0, dy=0):
        x = eval(xml.attrib.get('x', '0')) + dx
        y = eval(xml.attrib.get('y', '0')) + dy

        bx, by = x, y
        
        dr = xml.attrib.get('dir', 'h')
        mar = eval(xml.attrib.get('margin', '10'))

        maxes = [0, 0]
        ID = -1
        for el in xml:
            if el.tag == 'vector':

                # if ID in self.elements.keys():
                #     # сдвиг главной оси на размер элемента
                #     w, h = self.elements[ID].getSize()
                #     if dr == 'h': x += w + mar
                #     elif dr == 'v': y += h + mar
                
                ox, oy = self.parse_vector(win, el, x, y)

                # поиск максимума из вложенных vector
                if maxes[0] < ox-x: maxes[0] = ox-x
                if maxes[1] < oy-y: maxes[1] = oy-y

                if dr == 'h': x = ox + mar
                if dr == 'v': y = oy + mar

                ID = -1
                   
        
            elif el.tag == 'offset':
                raise Exception("You can not use <offset> inside <vector>")

            elif el.tag == 'default':
                self.defattrs = el.attrib
            elif el.tag == 'win':
                bg = eval(el.attrib.get('bg', '[230]*3'))
                win.bg = bg
            elif el.tag == 'frozen':
                self.parse_frozen(win, el, x, y)
            else:

                ID = self.parse_element(win, el, x, y)

                w, h = self.elements[ID].getSize()
                sx, sy = self.elements[ID].getStart()
                if dr == 'h': x = sx + w
                elif dr == 'v': y = sy + h

                if ID in self.elements.keys():
                    # поиск максимальных значений
                    w, h = self.elements[ID].getSize()
                    if w > maxes[0]: maxes[0] = w
                    if h > maxes[1]: maxes[1] = h

                if dr == 'h': x += mar
                if dr == 'v': y += mar

        
        # сдвиг побочной оси при завершении парсинга vector
        if dr == 'h': y = by + maxes[1]
        elif dr == 'v': x = bx + maxes[0]

        return [x, y]
    

    def parse_frozen(self, win, xml:Element, dx=0, dy=0):
        for el in xml:
            # if el.tag in ['vector', 'offset', 'fixed']:
            #     raise Exception("You cannot put the following tags in <fixed>: (<offset>, <vector>, <fixed>)")
            if el.tag == 'vector':
                print(dx, dy)
                self.parse_vector(win, el, dx, dy)
            else:
                self.parse_element(win, el, dx, dy)
        return [dx, dy]
    
            

    def get_design(self, win) -> dict:

        root = ET.fromstring(self.str_xml)
        self.parse_offset(win, root)

        return self.elements