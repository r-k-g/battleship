from fltk import *

class GameEndWin(Fl_Window):
    """Notification of win or loss at end of battleship game."""

    def __init__(self, victory, gamewin):
        """Initialize an instance.
        
        Victory is whether game was won and gamewin is BattleWin window.
        """

        w, h = 270, 150
        super().__init__(w, h, 'Game Over')

        self.set_modal()

        self.gamewin = gamewin

        msgbox = Fl_Box(30, 30, w-60, h-60)
        text = 'GAME WON!' if victory else 'GAME LOST...'
        msgbox.label(text)

        self.close_but = Fl_Button(w-100, h-50, 80, 38, 'Close')
        self.close_but.callback(self.hide)
    
    def hide(self, wid=None):
        """Close window and disconnect parent gamewin."""

        self.gamewin.disconn_cb(0)
        super().hide()