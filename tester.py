from fltk import *
import random as r

EVENTNAMES = {
    0: 'FL_NO_EVENT',
    1: 'FL_PUSH', 
    2: 'FL_RELEASE', 
    3: 'FL_ENTER', 
    4: 'FL_LEAVE', 
    5: 'FL_DRAG', 
    6: 'FL_FOCUS', 
    7: 'FL_UNFOCUS', 
    8: 'FL_KEYDOWN', 
    9: 'FL_KEYUP', 
    10: 'FL_CLOSE', 
    11: 'FL_MOVE', 
    12: 'FL_SHORTCUT', 
    13: 'FL_DEACTIVATE', 
    14: 'FL_ACTIVATE', 
    15: 'FL_HIDE', 
    16: 'FL_SHOW', 
    17: 'FL_PASTE', 
    18: 'FL_SELECTIONCLEAR', 
    19: 'FL_MOUSEWHEEL', 
    20: 'FL_DND_ENTER', 
    21: 'FL_DND_DRAG', 
    22: 'FL_DND_LEAVE', 
    23: 'FL_DND_RELEASE', 
    24: 'FL_SCREEN_CONFIGURATION_CHANGED', 
    25: 'FL_FULLSCREEN', 
    26: 'FL_ZOOM_GESTURE', 
    27: 'FL_EVENT_27', 
    28: 'FL_EVENT_28', 
    29: 'FL_EVENT_29', 
    30: 'FL_EVENT_30'
}


class TestWin(Fl_Double_Window):
    def __init__(self, w, h, title='Tester'):
        super().__init__(w, h, title)

        Fl.add_handler(self.myfunc)
        self.resizable(self)
    
    def func(self):
        pass

    def handle(self, event):
        ret = super().handle(event)
        return ret
    
    def draw(self):
        super().draw()

    def hide(self):
        super().hide()
    
    def myfunc(self, event):
        print(event)
        if event == FL_FULLSCREEN:
            print('fullscreened or unfullscreened')
            return 1
        else:
            return 0

win = TestWin(700, 500)
win.show()
Fl.run()