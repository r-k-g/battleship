from fltk import *

import window

def main():
    win = window.BattleWin(900, 600)
    win.show()
    Fl.run()

if __name__ == "__main__":
    main()