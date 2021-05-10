from fltk import *

import pickle
import socket

class Server:
    """TCP server to host a game, send and receive data between
    two games."""

    def __init__(self, gamewin, host='0.0.0.0', port=42069):
        """Initialize an instance.
        
        gamewin is a BattleWin window.
        """

        self.gamewin = gamewin
        self.conn = None

        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.s.bind((host, port))
        self.s.listen(1)
        self.fdl = self.s.fileno()

        Fl.add_fd(self.fdl, self.accept_connections)
    
    def accept_connections(self, fdl):
        """Accept a connection."""

        self.conn, raddr = self.s.accept()
        self.fd = self.conn.fileno()

        Fl.add_fd(self.fd, self.receive_data)

        self.gamewin.connected_cb()

    def receive_data(self, fd):
        """Receive data from a connection."""

        data = self.conn.recv(1024)
        
        # Close connection if receiving close message
        if data == b'':
            self.gamewin.disconn_cb(0)
            self.conn = None
        
        else: # Send to gamewin
            self.gamewin.recv_data(pickle.loads(data))
    
    def send_data(self, data):
        """Send passed data to connection."""
        self.conn.sendall(pickle.dumps(data))
    
    def close(self):
        """Close the connection.
        
        There might be a bug or two somewhere here, I had to do a lot
        of experimentation to not get errors.
        """

        try:
            self.s.close()
        except Exception as e:
            print(e)
        if self.conn is not None:
            self.conn.close()
            Fl.remove_fd(self.fd)

        Fl.remove_fd(self.fdl)


class Client:
    """TCP client to send and receive data with a game."""

    def __init__(self, gamewin, host='localhost', port=42069):
        """Initialize an instance.
        
        gamewin is a BattleWin window.
        """

        self.gamewin = gamewin

        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.s.connect((host, port))
        self.fd = self.s.fileno()

        Fl.add_fd(self.fd, self.receive_data)

    def receive_data(self, fd):
        """Receive data from connection."""

        data = self.s.recv(1024)
        
        # Close connection if receiving close message
        if data == b'':
            self.gamewin.disconn_cb(0)
        
        else: # Send to gamewin
            self.gamewin.recv_data(pickle.loads(data))
    
    def send_data(self, data):
        """Send passed data to connection."""
        self.s.sendall(pickle.dumps(data))
    
    def close(self):
        """Close the connection.
        
        There might be a bug or two somewhere here, I had to do a lot
        of experimentation to not get errors.
        """

        try:
            self.s.close()
            Fl.remove_fd(self.fd)
        except Exception:
            print('closing without a connection')
        