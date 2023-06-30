
from .xml_parser import Parser
from .window import Window

class App:

    def __init__(self):
        '''
        WIN_SIZE = (width, height)\n
        ONCLICK = {'id кнопки' : [функция, (аргументы)]}\n
        DESIGN = "src/<файл дизайна>.xml"\n
        XML_CONTENT_DESIGN = "<?xml version="1.0" encoding="utf-8"?>...", xml дизайн в str\n
        XML_VIEWS = {"my_view_tag" : myView}, здесь опредеять пользовательские элементы дизайна, 
        где my_view_tag - тэг в xml, myView - класс
        '''
        self.WIN_SIZE = (800,500) # размер окна
        self.PROGRAM_NAME = "Ezzgui Project"
        self.VIEWS:dict = {} # 
        self.ONCLICK:dict = {} # связи id кнопок с функциями на нажатие {'id':[func, (*args)]}
        self.DESIGN = "" # файл с дизайном
        self.XML_DESIGN_CONTENT = "" # строка с содержимым как в файле дизайна
        # для пользовательских элементов дизайна
        self.XML_VIES = {} # {'canvas':Canvas, ...}
        self.win:Window = None

    def on_create(self):
        '''Функция выполнится до запуска цикла приложения
        
        Может использоваться для:
        * инициализации побочных страниц приложения
        * инициализации объектов <table> и <ScrollView>'''
        ...

    def load_design(self):
        '''Формирует дизайн из xml и размещает на окне'''
        if self.XML_DESIGN_CONTENT == '':
            with open(self.DESIGN, encoding='utf-8') as f:
                xml_content = f.read()
        else:
            xml_content = self.XML_DESIGN_CONTENT
        parser = Parser(xml_content)
        parser.XML_VIEWS = self.XML_VIES
        self.VIEWS = parser.get_design(self.win)

        for (key, view) in self.VIEWS.items():
            if key in self.ONCLICK.keys():
                view.on_click_func = self.ONCLICK[key]

        self.win.design = self.VIEWS
