
import pygame
import os
import cv2
import numpy as np
from PIL import Image, ImageEnhance, ImageFilter

from ezzgui.app import App
from ezzgui.imports import *
from ezzgui.window import Window
from ezzgui.scroll import ScrollView

from .seekbar import SeekBar
from .image_view import ImageView



class ComparedCoinItem:
    def __init__(self, img, name, name_catalog, foldername_catalog, similar):
        self.img = img
        self.name = name
        self.name_catalog = name_catalog.split('.')[0]
        self.foldername_catalog = foldername_catalog
        self.similar = similar


class CatalogPage(App):
    def __init__(self, base):
        super().__init__()
        self.base = base
        self.win = self.base.win
        self.DESIGN = "src/xml/catalog_page.xml"
        self.XML_VIES = {
            'SeekBar' : SeekBar,
            'ImageView' : ImageView
        }
        self.ONCLICK = {
            'back' : [self.back, ()]
        }
        self.load_design()

        self.coinView = CoinView(self.VIEWS['compared'].get_surface())

    def back(self):
        self.base.win.design = self.base.VIEWS

    def load_data(self, folder):
        files = os.listdir(folder)
        # проверка
        files = [f for f in files if f.split('.')[-1] in ['png', 'jpg', 'jpeg']]
        

        catalog_imgs = {
            f : Image.open(f'{folder}/{f}')
            for f in files
        }

        catalog_converted_imgs = {
            k : img.resize(size=[120,120]).convert('L').filter(ImageFilter.CONTOUR)
            for k, img in catalog_imgs.items()
        }

        def convert(pg_img:pygame.Surface):
            [w, h] = pg_img.get_size()
            pixel_data = pygame.image.tostring(pg_img, 'RGBA')
            return Image.frombytes('RGBA', (w, h), pixel_data)
            
        imkeys = [k.split('_')[-1] for k in self.base.coinPage.VIEWS.keys() if 'img_' in str(k)]
        cur_imgs = {
            self.base.coinPage.VIEWS[f'name_{k}'].get_text() : convert(self.base.coinPage.VIEWS[f'img_{k}'].img)
            for k in imkeys
        }

        cur_converted_imgs = {
            k : img.resize(size=[120,120]).convert('L').filter(ImageFilter.CONTOUR)
            for k, img in cur_imgs.items()
        }

        # print(catalog_imgs)
        # print(cur_imgs)

        ccis = []
        for ki, img in cur_converted_imgs.items():
            mx = 0
            kidx = 0
            for kj, cimg in catalog_converted_imgs.items():
                similar = CatalogPage.compare(img, cimg)
                if similar > mx:
                    mx = similar
                    kidx = kj
            ccis.append(ComparedCoinItem(cur_imgs[ki], ki, kidx, f'{folder}/{kidx}', mx))

        self.coinView.reload(ccis)
        self.VIEWS['compared'].set_elements(self.coinView.VIEWS)


        
    @staticmethod
    def compare(img1, img2):
        arr1 = np.array(img1)
        arr2 = np.array(img2)

        # Преобразование в формат CV_32F и одноканальные изображения
        cvimg1 = arr1.astype(np.float32)
        cvimg2 = arr2.astype(np.float32)

        # Вычисление гистограмм
        histogram1 = cv2.calcHist([cvimg1], [0], None, [256], [0, 256])
        histogram2 = cv2.calcHist([cvimg2], [0], None, [256], [0, 256])

        # Нормализация гистограмм
        cv2.normalize(histogram1, histogram1, 0, 1, cv2.NORM_MINMAX)
        cv2.normalize(histogram2, histogram2, 0, 1, cv2.NORM_MINMAX)

        # Сравнение гистограмм
        similar = cv2.compareHist(histogram1, histogram2, cv2.HISTCMP_CORREL)
        return similar



class Win:
    def __init__(self, win): self.win = win

class CoinView(App):
    def __init__(self, surf):
        super().__init__()
        self.win = Win(surf)
        self.XML_VIES = {
            'ImageView' : ImageView
        }
        # self.reload(CCIs)

    def reload(self, CCIs):

        # очистка папки edit_imgs
        path = 'src/edit_imgs'
        file_list = os.listdir(path)
        for file in file_list:
            file_path = os.path.join(path, file)
            os.remove(file_path)

        # заполнение edit_imgs
        for cci in CCIs:
            im:Image.Image = cci.img
            im.save(f'src/edit_imgs/{cci.name}.png')
            cci.foldername = f'src/edit_imgs/{cci.name}.png'

        self.XML_DESIGN_CONTENT = '''<?xml version="1.0" encoding="utf-8"?>
        <offset x="10" y="10">
            <default font="Courier"/>
            <vector dir="v">
                {}
            </vector>
        </offset>
        '''.format(''.join([
            f'''<vector margin="30">
                <vector>
                    <ImageView file="{cci.foldername}" size="120"/>
                    <vector margin="5" dir="v">
                        <text text="Название: " color="[70]*3"/>
                        <text text="{cci.name if len(cci.name)<9 else cci.name[:7:]+'...'}"/>
                    </vector>
                </vector>
                
                <vector>
                    <ImageView file="{cci.foldername_catalog}" size="120"/>
                    <vector margin="15" dir="v">
                        <vector margin="0" dir="v">
                            <text text="Название в каталоге: " color="[70]*3"/>
                            <text text="{cci.name_catalog}"/>
                        </vector>
                        <vector margin="0" dir="v">
                            <text text="Степень схожести:" color="[70]*3"/>
                            <text text="{cci.similar}"/>
                        </vector>
                    </vector>
                </vector>

            </vector>'''
            for cci in CCIs
        ]))
        # print(self.XML_DESIGN_CONTENT)
        self.load_design()

