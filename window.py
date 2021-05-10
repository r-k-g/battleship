from fltk import *

from getpass import getuser

import grid, ship, network, game_end

class BattleWin(Fl_Double_Window):
    """Digital game of battleship.
    
    To be played with 2 computers over a local network, or on the same
    computer, though that's really just for testing.
    """

    def __init__(self, w, h):
        """Initialize an instance."""

        super().__init__(w, h, 'Battleship')
        
        # Index of boat currently being placed
        self.placing = -1

        # Various flags
        self.placed = False
        self.enemy_placed = False
        self.turn = False

        self.connection = None
        
        # Will be a list of boats once connected & enemy placed.
        self.enemy_boats = None

        self.begin()

        # Buttons for connecting/disconnecting to other games
        self.host_but = Fl_Button(30, 35, 140, 35, 'Host Game')
        self.host_but.callback(self.host_cb)
        self.host_but.clear_visible_focus()
        self.conn_but = Fl_Button(190, 35, 140, 35, 'Join Game')
        self.conn_but.callback(self.conn_cb)
        self.conn_but.clear_visible_focus()
        self.disconn_but = Fl_Button(350, 35, 140, 35, 'Disconnect')
        self.disconn_but.callback(self.disconn_cb)
        self.disconn_but.clear_visible_focus()

        # Label players
        self.pname_label = Fl_Box(0, 70, 30, h-140, '\n'.join(list(getuser().upper())))
        self.ename_label = Fl_Box(w-30, 70, 30, h-140, 'E\nN\nE\nM\nY')
        
        menuitems = (
            ('Game', 0, 0, 0, FL_SUBMENU),
                ('Host Game', 0, self.host_cb),
                ('Join Game', 0, self.conn_cb),
                ('Disconnect', 0, self.disconn_cb),
                (None, 0)
        )
        
        self.menubar = Fl_Menu_Bar(-1, -1, w + 2, 31)
        self.menubar.copy(menuitems)
        
        # Has both player grid and enemy grid
        self.resize_grids = ResizeGrids(30, 100, w-60, h-130, self)
        self.resizable(self.resize_grids)
        
        self.boatgroup = Fl_Group(30, 30, 5, 5)

        # Put invisible boats to be placed on an unimportant starting tile
        self.boats = [ship.Ship(i, self.resize_grids.enemy_grid.tiles[0][0]) for i in range(1, 5)]
        self.boatgroup.end()
        self.boatgroup.resizable(None)

        # For status/instructions messages
        self.status_box = Fl_Box(20, h-35, w-40, 30)
        self.status_box.label('Host a game or join an game to start.')

        self.end()

        # Has to be after self.resize_grids
        c = self.resize_grids.player_grid.c
        r = self.resize_grids.player_grid.r
        self.hit_list = [[0 for i in range(c)] for x in range(c)]
        self.e_hit_list = [[0 for i in range(c)] for x in range(c)]

        self.size_range(510, 330)
    
    def connected_cb(self):
        """Change label and send username once connected."""

        if isinstance(self.connection, network.Server):
            self.host_but.label('CONNECTED')
            self.status_box.label('Connected. Place your boats in the left grid.')

            self.connection.send_data(getuser())

            # Start placing boats
            self.start_placing()

    def host_cb(self, wid=None):
        """Host a game."""

        # Create server
        self.connection = network.Server(self)

        # Deactivate options
        self.conn_but.deactivate()
        self.menubar.find_item('Game/Join Game').deactivate()
        self.host_but.deactivate()
        self.menubar.find_item('Game/Host Game').deactivate()

        self.host_but.label('WAITING...')
        self.status_box.label('Waiting for a connection.')

    def conn_cb(self, wid=None):
        """Join an existing game."""

        # Get IP
        host = fl_input('Enter host IP:', 'localhost').strip() or 'localhost'

        try:
            self.connection = network.Client(self, host=host)
        except ConnectionRefusedError: # Works on windows, might be different on other platforms
            m = 'ERROR CONNECTING:\nEnsure other player has clicked host game and check IP + ports.'
            fl_alert(m)
            return 0
        
        # Deactivate options
        self.host_but.deactivate()
        self.menubar.find_item('Game/Host Game').deactivate()
        self.conn_but.deactivate()
        self.menubar.find_item('Game/Join Game').deactivate()

        self.status_box.label('Connected. Place your boats in the left grid.')

        # Send username and start placing boats
        self.connection.send_data(getuser())
        self.start_placing()

    def disconn_cb(self, wid=None):
        """Disconnect from another game if connected and reset the game."""


        # Close connection if necessary
        if self.connection is not None:
            self.connection.close()
            self.connection = None
        
        # Reactivate network options
        self.host_but.activate()
        self.menubar.find_item('Game/Host Game').activate()
        self.conn_but.activate()
        self.menubar.find_item('Game/Join Game').activate()
        self.host_but.label('Host Game')
        self.ename_label.label('E\nN\nE\nM\nY')

        self.status_box.label('Host a game or join an game to start.')

        self.reset_game()

    def recv_data(self, data):
        """Receive data from the connected game"""

        # Initial username
        if isinstance(data, str):
            if data == getuser():
                data += '2'
            self.ename_label.label('\n'.join(list(data.upper())))

        # Receiving enemy boat locations
        elif not self.enemy_placed:
            self.get_enemy_boats(data)
        
        else: # Updating hits and misses
            self.hit_list = data
            self.resize_grids.player_grid.update_visuals(self.hit_list)
            self.update_boat_hits()
            self.turn = True
            self.status_box.label('Choose a tile in the rightmost grid to attack.')

    def reset_game(self):
        """Reset the game."""

        self.turn = False
        self.enemy_placed = False
        self.placed = False
        self.placing = -1
        

        # Rather hacky stuff going on here
        # because deleting widgets is a pain and wasn't working
        # Basically set retired flag and just ignore retired boats,
        # new games will just keep creating more and more enemy boats
        if self.enemy_boats is not None:
            for b in self.enemy_boats:
                b.tile = self.resize_grids.enemy_grid.tiles[0][0]
                b.placed = False
                b.valid = False
                b.hits = [False] * b.length
                b.horizontal = True
                b.retired = True
                b.hide()

        # Reset boats
        for b in self.boats:
            b.tile = self.resize_grids.enemy_grid.tiles[0][0]
            b.placed = False
            b.valid = False
            b.hits = [False] * b.length
            b.horizontal = True
            b.hide()

        c = self.resize_grids.player_grid.c
        r = self.resize_grids.player_grid.r
        self.hit_list = [[0 for i in range(c)] for x in range(c)]
        self.e_hit_list = [[0 for i in range(c)] for x in range(c)]

        self.resize_grids.player_grid.update_visuals(self.hit_list)
        self.resize_grids.enemy_grid.update_visuals(self.e_hit_list)

        self.ename_label.label('E\nN\nE\nM\nY')

    def get_enemy_boats(self, boats):
        """Create enemy boats off of data connected game has sent."""

        self.enemy_placed = True
        tiles = self.resize_grids.enemy_grid.tiles
        
        self.boatgroup.begin()

        # When game gets reset, old enemy boats are kept to avoid deletion problems
        # So need to add to list and not reset
        if self.enemy_boats is None:
            self.enemy_boats = [ship.Ship(b[0], tiles[b[2]][b[1]], b[3]) for b in boats]
        else:
            self.enemy_boats.extend([ship.Ship(b[0], tiles[b[2]][b[1]], b[3]) for b in boats])
        
        for b in self.enemy_boats:
            b.valid = True
            b.placed = True
            x, y = b.tile.x_ind, b.tile.y_ind
            b.locations = [(x+i, y) if b.horizontal else (x, y+i) for i in range(b.length)]

        self.boatgroup.end()

        # Start the game if self boats placed as well
        if self.placed:
            self.start_game()

    def start_placing(self):
        """Start placing of boats."""
        self.placing = 0
        self.boats[self.placing].show()
    
    def place_boat(self):
        """Place the current boat if it is valid."""

        boat = self.boats[self.placing]
        if self.resize_grids.player_grid.wid_in(boat.tile):
            if self.boat_validpos() and not self.boat_overlap():
                
                boat.placed = True
                x, y = boat.tile.x_ind, boat.tile.y_ind
                boat.locations = [(x+i, y) if boat.horizontal else (x, y+i) for i in range(boat.length)]
                
                # Just in case
                boat.valid = True
                boat.show()
                
                # Move on to the next boat
                if self.placing < len(self.boats) - 1:
                    wid = Fl.belowmouse()
                    if isinstance(wid, grid.Tile):
                        self.boats[self.placing+1].tile = wid
                    self.placing += 1
                
                # Wait for opponent or start game if all placed
                else:
                    self.all_placed()
                    
    def all_placed(self):
        """Stop placing of boats/set flags, start game if opponent ready."""

        self.placing = -1
        self.placed = True

        boats = [(b.length, b.tile.x_ind, b.tile.y_ind, b.horizontal) for b in self.boats]
        self.connection.send_data(boats)

        # Start game if enemy has also placed their boats
        if self.enemy_boats is not None and not all([b.retired for b in self.enemy_boats]):
            self.start_game()
        else:
            self.status_box.label('All placed. Waiting for your opponent to place their ships.')

    def start_game(self):
        """Start a game, server always goes first."""

        # Server goes first
        if isinstance(self.connection, network.Server): # TODO add random turn choice
            self.turn = True
        
        if self.turn:
            self.status_box.label('Choose a tile in the rightmost grid to attack.')
        else:
            self.status_box.label('Waiting for your opponent to take their turn.')

    def tile_clicked(self, tile):
        """Check validity of a tile click and respond accordingly."""

        if self.turn:
            if self.resize_grids.enemy_grid.wid_in(tile):
                x, y = tile.x_ind, tile.y_ind # For convenience

                # Don't do anything if already clicked
                if self.e_hit_list[y][x] != 0: 
                    return
                
                for b in self.enemy_boats:
                    if b.retired: continue # Part of hack to make resetting work

                    if (x, y) in b.locations:
                        self.e_hit_list[y][x] = 2
                        self.hit_boat(b)
                        break
                else: # MISS
                    self.e_hit_list[y][x] = 1
                
                self.connection.send_data(self.e_hit_list)
                self.resize_grids.enemy_grid.update_visuals(self.e_hit_list)
                self.turn = False
                self.status_box.label('Waiting for your opponent to take their turn.')

    def hit_boat(self, boat):
        """Respond to a hit on an enemy boat."""

        # Doesn't actually matter where the boat gets hit because
        # it won't get shown until it's all hit
        for h in range(len(boat.hits)):
            if not boat.hits[h]:
                boat.hits[h] = True
                break
        
        if all(boat.hits): # Boat completely hit, "destroyed"
            boat.show()
            self.check_gameover()

    def update_boat_hits(self):
        """Update where player boats are hit."""

        # Get all coordinates of hits
        hitcoords = list()
        for y in range(len(self.hit_list)):
            for x in range(len(self.hit_list[0])):
                if self.hit_list[y][x] == 2:
                    hitcoords.append((x, y))
        
        # Check all coordinates with boat coordinates
        for b in self.boats:
            for loc in range(len(b.locations)):
                # Precise location of hit matters unlike with enemy boats
                if b.locations[loc] in hitcoords:
                    b.hits[loc] = True
        self.check_gameover()

    def check_gameover(self):
        """Check if the game is over, and respond to win/loss."""

        # Check player boats
        for b in self.boats:
            if not all(b.hits):
                break
        else:
            self.gameover(False)

        # Check enemy boats
        for b in self.enemy_boats:
            if b.retired: # Ignore retired boats, part of resetting hack
                continue
            if not all(b.hits):
                break
        else:
            self.gameover(True)

    def gameover(self, victory):
        """End the game and show popup according to win/loss."""
        end_message = game_end.GameEndWin(victory, self)
        end_message.show()

    def handle(self, event):
        """Handle events for window.
        
        Extended to handle rotating and placing of boats."""


        ret = super().handle(event)
        
        if event == FL_PUSH: # Rotate current boat
            if Fl.event_button3() and self.placing >= 0:
                self.boats[self.placing].rotate()  
                self.boats[self.placing].redraw()
        
        # "Preview" of where boat will be placed
        elif event == FL_MOVE:
            if self.placing >= 0:
                
                wid = Fl.belowmouse()
                boat = self.boats[self.placing]

                grids = (
                   self.resize_grids.player_grid.wid_in(wid),
                   self.resize_grids.enemy_grid.wid_in(wid)
                )
                
                if any(grids):
                    if not boat.visible():
                        boat.show()
                    
                    # Check validity if on right grid, auto False otherwise
                    boat.valid = self.valid_boat() if grids[0] else False
                    
                    if boat.tile != wid:
                        boat.tile = wid
                    boat.redraw()
                
                # Hide the boat if it mouse isn't in any grid
                else:
                    if boat.valid:
                        boat.valid = False
                    boat.hide()
                
        return ret
    
    def boat_validpos(self):
        """Return true if the current placing boat isn't too near the edge."""

        boat = self.boats[self.placing]
        
        x, y = boat.tile.x_ind, boat.tile.y_ind
        
        # Assumes equal # rows and columns
        dim = self.resize_grids.player_grid.r
        
        if boat.horizontal:
            return x + boat.length <= dim
        else:
            return y + boat.length <= dim
    
    def boat_overlap(self):
        """Return true if the current placing boat is overlapping with another.
        
        I think I wrote this code before I made ships have a locations list
        but it works so I'm too scared to change it now.
        """

        boat = self.boats[self.placing]
        
        # Get all locations of current boats
        locations = set()
        for b in self.boats:
            if b != boat and b.placed:
                x, y = b.tile.x_ind, b.tile.y_ind
                
                for i in range(b.length):
                    locations.add((x+i, y) if b.horizontal else (x, y+i))
        
        # Get locations of current boat
        boat_locations = set()            
        x, y = boat.tile.x_ind, boat.tile.y_ind
        for i in range(boat.length):
            boat_locations.add((x+i, y) if boat.horizontal else (x, y+i))
        
        # Check for overlap
        return bool(locations & boat_locations)
    
    def valid_boat(self):
        """Return true if the current placing boat is in a valid location.
        
        Doesn't check that it's in the right grid.
        """

        boat = self.boats[self.placing]

        return self.boat_validpos() and not self.boat_overlap()

    def draw(self):
        """Add a whole ton of redrawing to make resizing work."""
        
        super().draw()

        # This causes some annoying flickering on linux/school computers 
        # but actually looks perfectly fine on windows
        Fl.add_timeout(0, self.redraw)

    def hide(self):
        """Close the connection before hiding."""
        if self.connection is not None:
            self.connection.close()
        
        super().hide()

class ResizeGrids(Fl_Group):
    """Group with grids for BattleWin window.
    
    Manages resizing and repositioning of grids, albeit badly.
    """

    def __init__(self, x, y, w, h, gamewin):
        """Initialize an instance.
        
        Arg "gamewin" is parent BattleWin window.
        """

        super().__init__(x, y, w, h)
        
        # Get starting positions and dimensions
        dim = self.getdim()
        startx = self.x() + round((self.w() - (dim*2 + 25)) / 2)
        starty = self.y() + round((self.h() - dim) / 2)

        self.begin()
        
        # Create the grids
        self.player_grid = grid.Grid(startx, starty, dim, dim, 10, 10, gamewin)
        self.enemy_grid = grid.Grid(startx + (dim+25), starty, dim, dim, 10, 10, gamewin)

        self.end()

        self.resizable(None)
    
    def draw(self):
        """Center and resize child grids properly.
        
        Assumes both grids have the same dimensions.
        """
    
        super().draw()


        dim = self.getdim()
        
        # 25 px buffer in between grids
        startx = self.x() + round((self.w() - (dim*2 + 25)) / 2)
        starty = self.y() + round((self.h() - dim) / 2)

        self.player_grid.resize(startx, starty, dim, dim)
        self.enemy_grid.resize(startx + (dim+25), starty, dim, dim)
    
    def getdim(self):
        """Return the max dimension of each child grid for current size.
        
        Assumes square grids.
        """

        # 25 px vert buffer in between grids
        dim = (self.w() - 25) // 2
        
        if dim > self.h():
            dim = self.h()
        
        return dim