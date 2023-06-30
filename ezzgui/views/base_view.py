
class BaseView:
    def getStart(self):
        '''Получение начальных координат'''
        raise Exception('You must override getStart()')
    
    def getSize(self):
        '''Получение размера view'''
        raise Exception('You must override getSize()')
    
    def spawn(self, events, mpos, mpress, keys, **kwargs) -> bool:
        '''Отображение и функционал элемента\n
        events - события окна pygame\n
        mpos - координаты курсора мыши\n
        mpress - зажатие кнопок мыши\n
        keys - зажатые клавиши клавиатуры

        retrun захват мыши (прокручивался ли объект)
        '''
        raise Exception('You must override spawn(self, events, mpos, mpress, keys, **kwargs) -> bool')