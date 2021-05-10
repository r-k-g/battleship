from fltk import *

class Ship(Fl_Box):
    """Visual representation of a ship in a battleship game."""

    def __init__(self, length, tile, orient_h=True):
        """Initialize an instance.
        
        Length is the number of tiles the ship takes up
        Tile is Anchoring top left tile ship is in
        Orient_h is whether ship is oriented vertically or horizontally
        """


        super().__init__(tile.x(), tile.y(), (tile.w()*length), tile.h())
        
        # "Anchor" tile, the top left tile ship is in
        self.tile = tile
        
        # For determining color if valid position or not
        self.valid = False
        self.placed = False

        # Hack to try and get resetting to work
        self.retired = False
        
        self.length = length
        self.horizontal = orient_h
        
        # To be filled by game window, list of all tile coords that
        # ship is in 
        self.locations = list()

        # Where the ship is hit, for drawing hits
        self.hits = [False] * self.length

        self.hide()
    
    def draw(self):
        """Draw the boat and appropriate hit markers"""

        super().draw()
        
        
        # Dimension of tile, assumes square tiles
        dim = self.tile.w()
        half = round(dim / 2)
        
        x, y = self.tile.x(), self.tile.y()
        
        if self.horizontal:
            w, h = dim*self.length, dim
        else:
            w, h = dim, dim*self.length
        
        # Colour ship red if invalid position
        if self.valid:
            fl_color(FL_DARK3)
        else:
            fl_color(FL_RED)
        
        # Draw boat rectangle
        fl_rectf(self.x()+4, self.y()+4, w-8, h-8)

        fl_color(FL_RED)

        # Draw all applicable hit markers
        for i in range(len(self.hits)):
            if self.hits[i]:
                if self.horizontal:
                    x_pos = self.x() + (dim*i) + 7
                    y_pos = self.y() + 7
                else:
                    x_pos = self.x() + 7
                    y_pos = self.y() + (dim*i) + 7
                
                fl_pie(x_pos, y_pos, dim-14, dim-14, 0.0, 360.0)

        self.resize(x, y, w, h)
            
    def rotate(self):
        """Rotate the boat."""
        self.size(self.h(), self.w())
        self.horizontal = not self.horizontal