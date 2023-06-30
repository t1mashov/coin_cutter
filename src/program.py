
import pygame
import ctypes
from PIL import Image

from tkinter import Tk, filedialog
from ezzgui.app import App
from ezzgui.imports import *
from ezzgui.window import Window
from ezzgui.scroll import ScrollView

from .seekbar import SeekBar
from .image_view import ImageView

from .cut import Cutter
from .align import AutoAlign

from .catalog import CatalogPage


class Program(App):
    def __init__(self):
        super().__init__()
        self.WIN_SIZE = (850,500)
        self.PROGRAM_NAME = 'Coin Cutter'
        self.DESIGN = "src/xml/main_page.xml"
        self.ONCLICK = {
            'load' : [self.load_scan, ()],
            'cut' : [self.cut, ()],
            'align' : [self.auto_align, ()],
            '+' : [self.change_zoom, (2,)],
            '-' : [self.change_zoom, (0.5,)],
            'catalog' : [self.to_catalog_page, ()],
            'save' : [self.save, ()],
        }
        self.XML_VIES = {
            'SeekBar' : SeekBar
        }

        self.scan_path = ''

        # кол-во вырезанных монет
        self.coins_len = 0
        # индекс выделенной монеты
        self.selected_coin = -1
        # масштаб
        self.zoom = 1
        # что находится на странице монет (ничего, скан, вырезанные монеты)
        self.coinPageOption = 'null'

        # объект страницы с монетами
        self.coinPage:CoinPage = None
        # объект страницы со сканом
        self.scan:ScanPage = None

        self.catalogPage = None

    
    def on_create(self):
        # страница каталога
        self.catalogPage = CatalogPage(self)
        
        super().load_design()
        
        # страница настройки монеты
        self.coinSettingsPage = CoinSettingsPage(self.VIEWS['settings'].get_surface())
        # страница ошибки, что монета не выбрана
        self.noCoinErrorPage = NoCoinErrorPage(self.VIEWS['settings'].get_surface())
        
        self.scanSettings = ScanLoadSettingsPage(self.VIEWS['settings'].get_surface())
        self.alignSettings = AlignCoinsSettingsPage(self.VIEWS['settings'].get_surface())
        self.coinSettingsVIEWS = self.noCoinErrorPage.VIEWS


        self.coinPage = None # страница с вырезанными монетками

        self.VIEWS['settings'].set_elements(self.scanSettings.VIEWS)

        self.optionSettings = SettingsOption(
            self.VIEWS['option'].get_surface(),
            ['select', 'align', 'coin'],
            self.change_option,
        )
        self.VIEWS['option'].set_elements(self.optionSettings.VIEWS)

        # текущий выбор настроек
        self.curOption = 'select'


    def change_option(self, option):
        settings = {
            'select' : self.scanSettings.VIEWS,
            'align' : self.alignSettings.VIEWS,
            'coin' : self.coinSettingsVIEWS,
        }
        self.curOption = option
        self.VIEWS['settings'].set_elements(settings[option])
        
        

    def load_scan(self):
        self.coins_len = 0
        self.selected_coin = -1
        self.coinPage = None # обнуляем предыдущие монеты

        # на странице монет - скан
        self.coinPageOption = 'scan'

        root = Tk()
        root.withdraw()
        
        file_path = filedialog.askopenfilename()
        root.destroy()
        if file_path == '': return
        self.scan_path = file_path

        ctx:ScrollView = self.VIEWS['ctx']
        self.scan = ScanPage(ctx.get_surface(), file_path)
        self.scan.reload(self.zoom)
        ctx.set_elements(self.scan.VIEWS)

        self.coinSettingsVIEWS = self.noCoinErrorPage.VIEWS
        if self.curOption == 'coin':
            self.change_option('coin')

    def cut(self):
        if self.scan_path == '': return

        # на странице монет - монеты
        self.coinPageOption = 'coins'

        bright = self.scanSettings.VIEWS['bright'].getValue()
        blur = self.scanSettings.VIEWS['blur'].getValue()
        add_del_radius = self.scanSettings.VIEWS['add_del'].getValue()
        
        imgs = Cutter.generate(self.scan_path, bright, blur, add_del_radius)
        self.coins_len = len(imgs)
        
        ctx:ScrollView = self.VIEWS['ctx']
        self.coinPage = CoinPage(self, ctx.get_surface(), imgs, self.selelct_coin)
        self.coinPage.reload(self.zoom)
        ctx.set_elements(self.coinPage.VIEWS)


    # при нажатии на "автовыравнивание"
    def auto_align(self):
        if self.coinPage == None: return

        a_start = self.alignSettings.VIEWS['from'].getValue()
        a_end = self.alignSettings.VIEWS['to'].getValue()

        # print(len(self.coinPage.VIEWS))

        # for i in range(self.coins_len):
        for i, k in enumerate(self.coinPage.coins.keys()):
            a = AutoAlign.get_angle(self.coinPage.VIEWS[f'img_{k}'].base_img, a_start, a_end)
            self.coinPage.VIEWS[f'img_{k}'].rotate(a)
            # вывод процентов загрузки
            print(f'{round((i+1)/self.coins_len*100)}%')
            
        
        self.coinPage.reload(self.zoom)

        # print(len(self.coinPage.VIEWS))
        self.VIEWS['ctx'].set_elements(self.coinPage.VIEWS)
        ...


    # при нажатии на вырезанную монету
    def selelct_coin(self, coin):

        def on_change(imgID:str):
            img = self.coinPage.VIEWS[imgID]
            val = self.coinSettingsPage.VIEWS['angle'].getValue()
            self.coinSettingsPage.VIEWS['t_angle'].set_text(f"{val}")
            img.rotate(val)

        def change_radius(imgID:str):
            img = self.coinPage.VIEWS[imgID]
            radius = self.coinSettingsPage.VIEWS['radius'].getValue()
            self.coinSettingsPage.VIEWS['t_radius'].set_text(f"{radius}")
            img.circleLine.radius = radius


        def apply_radius(imgID:str):
            img:ImageView = self.coinPage.VIEWS[imgID]
            img.cut()
            

        def default(imgID:str):
            img:ImageView = self.coinPage.VIEWS[imgID]
            img.default()
            
        # перенос параметров из картинки на панель настроек
        self.coinSettingsPage.VIEWS['angle'].cursor = self.coinPage.VIEWS[f'img_{coin}'].angle + 180
        self.coinSettingsPage.VIEWS['t_angle'].set_text(f"{self.coinPage.VIEWS[f'img_{coin}'].angle}")
        self.coinSettingsPage.VIEWS['angle'].onChange = [on_change, (f'img_{coin}',)]

        self.coinSettingsPage.VIEWS['radius'].cursor = self.coinPage.VIEWS[f'img_{coin}'].circleLine.radius - self.coinSettingsPage.VIEWS['radius'].points[0]
        self.coinSettingsPage.VIEWS['t_radius'].set_text(f"{self.coinPage.VIEWS[f'img_{coin}'].circleLine.radius}")
        self.coinSettingsPage.VIEWS['radius'].onChange = [change_radius, (f'img_{coin}',)]

        self.coinSettingsPage.VIEWS['erase'].on_click_func = [apply_radius, (f'img_{coin}',)]
        self.coinSettingsPage.VIEWS['default'].on_click_func = [default, (f'img_{coin}',)]
        
        self.coinSettingsVIEWS = self.coinSettingsPage.VIEWS
        if self.curOption == 'coin':
            self.change_option('coin')

        self.selected_coin = coin
        # for i in range(self.coins_len):
        for i in self.coinPage.coins.keys():
            self.coinPage.VIEWS[f'img_{i}'].bg = None
        self.coinPage.VIEWS[f'img_{coin}'].bg = (120,200,120)
        # self.coinSettingsVIEWS = self.coinPage.VIEWS
        # print(coin)
        ...


    def to_catalog_page(self):
        root = Tk()
        root.withdraw()
        folder_path = filedialog.askdirectory()
        root.destroy()
        if folder_path == '': return
        if self.coinPage == None: return

        self.catalogPage.load_data(folder_path)
        self.win.design = self.catalogPage.VIEWS
        ...

    
    def save(self):
        root = Tk()
        root.withdraw()
        folder_path = filedialog.askdirectory()
        root.destroy()
        if folder_path == '': return

        imkeys = [k.split('_')[-1] for k in self.coinPage.VIEWS.keys() if 'img_' in str(k)]
        for k in imkeys:
            name = self.coinPage.VIEWS[f'name_{k}'].get_text()
            pygame.image.save(self.coinPage.VIEWS[f'img_{k}'].img, f'{folder_path}/{name}.png')
        ...

    
    def change_zoom(self, d):
        self.zoom *= d

        self.VIEWS['t_zoom'].set_text(f'{round(self.zoom*100)}%')

        dy = self.VIEWS['ctx'].dy
        
        # print(self.zoom, self.coinPageOption)
        if self.coinPageOption == 'scan':
            self.scan.reload(self.zoom)
            self.VIEWS['ctx'].set_elements(self.scan.VIEWS)
        elif self.coinPageOption == 'coins':
            self.coinPage.reload(self.zoom)
            self.VIEWS['ctx'].set_elements(self.coinPage.VIEWS)

        # прокрутка scroll до прежнего места
        # self.VIEWS['ctx'].dy = dy * d
        dy *= d
        W, H = self.VIEWS['ctx'].max_xy
        # print(dy/d, dy, H)
        if dy < -H:
            dy = -H
        self.VIEWS['ctx'].move(d=[0, dy])
        # print(self.VIEWS['ctx'].max_xy)
        # print('dy =',self.VIEWS['ctx'].dy)
        
        ...



class Win:
    def __init__(self, win): self.win = win

class CoinPage(App):
    def __init__(self, base:Program, surf:pygame.Surface, coins:list, on_click=lambda:...):
        # print(coins)
        super().__init__()
        self.win = Win(surf)
        self.base = base
        self.on_click = on_click
        self.resize = 1
        self.XML_VIES = {
            'ImageView' : ImageView
        }
        # self.coins = [coins[i:i+1:] for i in range(0, len(coins), 1)]
        self.coins = {str(i):c for i, c in enumerate(coins)}
        self.reload()

    def reload(self, resize=1):
        # сохранение углов монет при изменении размера
        # imkeys = []
        self.resize = resize
        old_resize = 1
        states = {}
        
        # imkeys = [c.split('.')[0].split('/')[-1] for c in self.coins]
        imkeys = list(self.coins.keys())
        if len(self.VIEWS) != 0:
            # imkeys = [k.split('_')[-1] for k in self.VIEWS.keys() if 'img_' in str(k)]
            # print(self.VIEWS)
            # imkeys = list(range(len(self.coins)))
            states = {
                key : {
                    'angle':self.VIEWS[f'img_{key}'].angle, 
                    'bg':self.VIEWS[f'img_{key}'].bg,
                    'base_img':self.VIEWS[f'img_{key}'].base_img,
                    'radius':self.VIEWS[f'img_{key}'].circleLine.radius,
                    'dirLine_pos':self.VIEWS[f'img_{key}'].dirLine.pos,
                    'circleLine_pos':self.VIEWS[f'img_{key}'].circleLine.pos,
                    'name' : self.VIEWS[f'name_{key}'].get_text()
                } for key in imkeys
            }
            old_resize = self.VIEWS[f'img_{imkeys[0]}'].resize
            

        self.XML_DESIGN_CONTENT = ('''<?xml version="1.0" encoding="utf-8"?>
        <offset x="20" y="0">
            <default font="Courier"/>
            <vector dir="v">
                <text text=" "/>''' +
                    ''.join([f'''
                    <vector>
                        <ImageView id="img_{i}" file="{file}" resize="{resize}" isButton="True"/>
                        <vector margin="5" dir="v">
                            <text text="Название:"/>
                            <input id="name_{i}" pos="[0,0,150,25]" size="15" bg="[230]*3" padding="2" text="{file.split('/')[-1].split('.')[0]}"/>
                            <button id="btn_{i}" text="Удалить" bgColor="[190]*3" hoverColor="[230]*3"/>
                        </vector>
                        <text text=" "/>
                    </vector>''' for i, file in self.coins.items()]) +
                '''
                <text text=" "/>
            </vector>
        </offset>''')

        # print(self.XML_DESIGN_CONTENT)

        # self.XML_DESIGN_CONTENT = ('''<?xml version="1.0" encoding="utf-8"?>
        # <offset x="20" y="0">
        #     <default font="Courier"/>
        #     <vector dir="v">
        #     <text text=" "/>''' +
            
        #     ''.join([
        #     '<vector>' +
        #         ''.join([f'''
        #             <ImageView id="img_{i}" file="{file}" resize="{resize}" isButton="True"/>
        #             <vector margin="5" dir="v">
        #                 <text text="Название:"/>
        #                 <input id="name_{i}" pos="[0,0,150,25]" size="15" bg="[230]*3" padding="2" text="{file.split('/')[-1].split('.')[0]}"/>
        #                 <button id="btn_{i}" text="Удалить" bgColor="[190]*3" hoverColor="[230]*3"/>
        #             </vector>
        #             <text text=" "/>''' for file in row]) +
        #      '</vector>' for i, row in enumerate(self.coins)]) +

        #     '''<text text=" "/>
        #     </vector>
        # </offset>''')
        self.load_design()

        # print(self.XML_DESIGN_CONTENT)

        # for i in range(len(self.coins)):
        for i in imkeys:
            self.VIEWS[f'img_{i}'].onclick = [self.on_click, (i,)]
            self.VIEWS[f'btn_{i}'].on_click_func = [self.delete, (i,)]
        
        # if imkeys != []:
            # print(states)
        for k, state in states.items():
            if f'img_{k}' in self.VIEWS.keys():
                self.VIEWS[f'img_{k}'].base_img = state['base_img']
                self.VIEWS[f'img_{k}'].circleLine.radius = state['radius']
                self.VIEWS[f'img_{k}'].dirLine.pos = state['dirLine_pos']
                self.VIEWS[f'img_{k}'].dirLine.pos[0] *= (resize / old_resize)
                self.VIEWS[f'img_{k}'].dirLine.pos[1] *= (resize / old_resize)
                self.VIEWS[f'img_{k}'].circleLine.pos = state['circleLine_pos']
                self.VIEWS[f'img_{k}'].circleLine.pos[0] *= (resize / old_resize)
                self.VIEWS[f'img_{k}'].circleLine.pos[1] *= (resize / old_resize)
                self.VIEWS[f'img_{k}'].rotate(state['angle'])
                self.VIEWS[f'img_{k}'].bg = state['bg']
                self.VIEWS[f'name_{k}'].set_content(state['name'])

    def delete(self, i):
        # print(self.coins)
        # print(i)
        del self.coins[i]
        # print(self.coins)
        self.reload(self.resize)
        self.base.VIEWS['ctx'].set_elements(self.VIEWS)
        ...



class ScanPage(App):
    def __init__(self, surf, scan:str):
        super().__init__()
        self.win = Win(win=surf)
        self.scan = scan
        self.XML_VIES = {
            'ImageView' : ImageView
        }
        self.reload()

    def reload(self, resize=1):
        self.XML_DESIGN_CONTENT = f'''<?xml version="1.0" encoding="utf-8"?>
        <offset x="0" y="0">
            <ImageView file="{self.scan}" resize="{resize}"/>
        </offset>'''
        super().load_design()


class ScanLoadSettingsPage(App):
    def __init__(self, surf):
        super().__init__()
        self.win = Win(win=surf)
        self.XML_VIES = {
            'SeekBar' : SeekBar
        }
        self.DESIGN = 'src/xml/scan_load_settings.xml'
        super().load_design()
        
        self.VIEWS['bright'].onChange = [lambda:self.VIEWS['t_bright'].set_text(f"{self.VIEWS['bright'].getValue()}"), ()]
        self.VIEWS['blur'].onChange = [lambda:self.VIEWS['t_blur'].set_text(f"{self.VIEWS['blur'].getValue()}"), ()]
        self.VIEWS['add_del'].onChange = [lambda:self.VIEWS['t_add_del'].set_text(f"{self.VIEWS['add_del'].getValue()}"), ()]


class AlignCoinsSettingsPage(App):
    def __init__(self, surf):
        super().__init__()
        self.win = Win(win=surf)
        self.XML_VIES = {
            'SeekBar' : SeekBar
        }
        self.DESIGN = 'src/xml/align_coins_settings.xml'
        super().load_design()

        self.VIEWS['from'].onChange = [lambda:self.VIEWS['t_from'].set_text(f"{self.VIEWS['from'].getValue()}"), ()]
        self.VIEWS['to'].onChange = [lambda:self.VIEWS['t_to'].set_text(f"{self.VIEWS['to'].getValue()}"), ()]



class CoinSettingsPage(App):
    def __init__(self, surf):
        super().__init__()
        self.win = Win(win=surf)
        self.XML_VIES = {
            'SeekBar' : SeekBar
        }
        self.DESIGN = 'src/xml/coin_settings.xml'
        super().load_design()


class NoCoinErrorPage(App):
    def __init__(self, surf):
        super().__init__()
        self.win = Win(win=surf)
        self.DESIGN = 'src/xml/no_coin_error.xml'
        super().load_design()


class SettingsOption(App):
    def __init__(self, surf, bids:list, on_click=lambda bid:(), defaultColor=[180]*3, pressedColor=[220]*3):
        super().__init__()
        self.win = Win(win=surf)
        self.bids = bids
        self.on_click = on_click
        self.defaultColor = defaultColor
        self.pressedColor = pressedColor
        self.DESIGN = 'src/xml/option_settings.xml'
        self.ONCLICK = {
            b : [self.onclick, (b,)]
            for b in self.bids
        }
        super().load_design()

    def onclick(self, bID):
        for bid in self.bids:
            self.VIEWS[bid].default_bg_color = self.defaultColor
            self.VIEWS[bid].on_focus_bg_color = self.defaultColor
        self.VIEWS[bID].default_bg_color = self.pressedColor
        self.VIEWS[bID].on_focus_bg_color = self.pressedColor
        self.on_click(bID)
