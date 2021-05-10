from fltk import *


class Grid(Fl_Group):
    """Grid of tiles in a battleship game."""

    def __init__(self, x, y, w, h, r, c, gamewin):
        """Initialize an instance.
        
        r and c are numbers of rows and columns respectively.
        gamewin is parent BattleWin window.
        """

        super().__init__(x, y, w, h)
        
        self.gamewin = gamewin
        
        self.tiles = list()
        self.r = r
        self.c = c
        
        # Assumes equal w & h, r & c
        self.dim = round(w / c)
        
        self.gentiles()
        
        self.end()

    def gentiles(self):
        """Generate self.r * self.c tiles and append lists of rows to self.tiles."""
        
        self.begin()
        
        col_list = list()
        
        start_x, start_y, = self.x(), self.y()
        
        # Assumes square Grid, equal # rows and columns
        self.dim = round(self.w() / self.c)
        
        for y in range(self.r):
            col_list = list()
            for x in range(self.c):
                x_pos, y_pos = start_x + (self.dim * x), start_y + (self.dim * y)
                col_list.append(Tile(x_pos, y_pos, self.dim, self.dim, self.gamewin, x, y))

            self.tiles.append(col_list)

        self.end()

    def draw(self):
        """Resize all tiles according to current size."""

        super().draw()
        
        self.dim = self.getdim()
        start_x, start_y, = self.x(), self.y()

        for y in range(self.r):
            for x in range(self.c):
                x_pos, y_pos = start_x + (self.dim * x), start_y + (self.dim * y)
                self.tiles[y][x].resize(x_pos, y_pos, self.dim, self.dim)

    def update_visuals(self, hit_list):
        """Update hits and misses among tiles according to passed list."""

        for y in range(self.r):
            for x in range(self.c):
                if hit_list[y][x] == 1: # Miss
                    self.tiles[y][x].miss = True
                elif hit_list[y][x] == 2: # Hit
                    self.tiles[y][x].hit = True
                else:
                    # So that this can reset
                    self.tiles[y][x].miss = False
                    self.tiles[y][x].hit = False
                
        self.redraw()

    def getdim(self):
        """Get the dimensions of one tile."""
        return round(self.w() / self.c)

    def wid_in(self, wid):
        """Return whether passed wid is in self.tiles."""
        
        for row in self.tiles:
            if wid in row:
                return True
        return False


class Tile(Fl_Button):
    """A tile that makes up grids in a battleship game."""

    def __init__(self, x, y, w, h, gamewin, x_ind, y_ind):
        """Initialize an instance.
        
        Gamewin is parent BattleWin window.
        x_ind and y_ind are coordinates of tile in grid.
        """

        super().__init__(x, y, w, h)

        self.gamewin = gamewin
        self.x_ind = x_ind
        self.y_ind = y_ind
        
        # Customize visuals
        self.box(FL_BORDER_BOX)
        self.color(FL_BLUE)
        self.clear_visible_focus()

        # Flags for drawing
        self.hit = False
        self.miss = False

    def handle(self, event):
        """Respond to events and update gamewin if necessary."""

        if event == FL_PUSH:
            if Fl.event_button1():
                if self.gamewin.placing >= 0:
                    self.gamewin.place_boat()
                
                else:
                    self.gamewin.tile_clicked(self)
            return 1
        
        if event == FL_DRAG:
            return 0
        
        return super().handle(event)

    def draw(self):
        """Extend Fl_Button draw to draw hit or miss markers."""

        super().draw()

        if self.hit or self.miss:
            # Change colour depending on hit or miss
            fl_color(FL_RED if self.hit else FL_WHITE)
            fl_pie(self.x()+4, self.y()+4, self.w() - 8, self.h() - 8, 0.0, 360.0)