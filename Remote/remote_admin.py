from typing import List, Tuple

from Common.board_position import BoardPosition
from Common.board_state import BoardState
from Common.color import ColorString
from Common.json_stream import NetworkJSONStream
from Common.player_interface import PlayerInterface
from Common.result import Result, ok
from Common.tiles import PortID, Tile, tile_to_tile_pattern, index_to_tile, port_id_to_network_port_id
from TestHarnesses.xboard import setup_board
from Common.util import timeout


class RemoteAdmin():
    """
    A module to represent a remote Administrator, handling all communication between referees
    and administrators on the server and the player on the client via a TCP connection. See ../Planning/remote.md for how the remote proxy pattern works. See https://felleisen.org/matthias/4500-f19/10.html for the format of all messages sent and received.

    Connections are closed when the tournament is over or if an error occurs with
    the Player or the TCP connection.
    """
    def __init__(self, player: PlayerInterface):
        self._player = player
         
    def connect_to_admin(self, host: str, port: int):
        """
        Use the given host and port to initiate a TCP connection to the server.
        """
        self._json_stream = NetworkJSONStream.tcp_client_to(host, port)
    
    def receive_messages(self):
        """
        Continually wait for messages and dispatch them to the player until the tournament is over. If the player doesn't receive a message from the server in 60 seconds,
        the player can assume it is a cheater and stop playing and close the connection.
        """
        self._tournament_incomplete = True
        while(self._tournament_incomplete):
            r_message = self._json_stream.receive_message()
            if r_message.is_ok():
                self.evaluate_message(r_message.value())
            else:
                self._tournament_incomplete = False
           

    def evaluate_message(self, message):
        """
        Call the appropriate function on the player based on the message type.
        """
        function = message[0]
        payload = message[1]
        if function == "playing-as":
            self._player.set_color(payload[0])
            self._json_stream.send_message("void")
        elif function == "others":
            self._player.set_players(payload)
            self._json_stream.send_message("void")
        elif function == "initial":
            action = self.handle_initial(payload)
            if action:
                self._json_stream.send_message(action)
        elif function == "take-turn":
            tile_pat = self.handle_intermediate(payload)
            if tile_pat:
                self._json_stream.send_message(tile_pat)
        elif function == "end-of-tournament":
            self._player.notify_won_tournament(payload[0])
            print(payload[0])
            self._json_stream.send_message("void")
            self._tournament_incomplete = False

    
    def handle_initial(self, initial) -> List:
        """
        Converts the initial tile message to a list of Tiles and a BoardState for the player.
        Returns the action the player takes in the format: [tile-pat, port, index, index]
        """
        board = setup_board(initial[0])
        board_state = board.get_board_state()
        tiles = [index_to_tile(initial[1]), index_to_tile(initial[2]), index_to_tile(initial[3])]
        
        r_move = self._player.generate_first_move(tiles, board_state)
        if r_move.is_ok():
            move = r_move.value()
            return [tile_to_tile_pattern(move[1]), port_id_to_network_port_id(move[2]), move[0].x, move[0].y]
        else:
            self._tournament_incomplete = False
            
    
    def handle_intermediate(self, intermediate) -> List:
        """
        Converts the intermediate tile message to a list of Tiles and a BoardState for the player.
        Returns the tile pattern representing hte move the player made in the format: [tile_index, rotation]
        """
        board = setup_board(intermediate[0])
        board_state = board.get_board_state()
        tiles = [index_to_tile(intermediate[1]), index_to_tile(intermediate[2])]

        r_move = self._player.generate_move(tiles, board_state)
        if r_move.is_ok():
            return tile_to_tile_pattern(r_move.value())
        else:
            self._tournament_incomplete = False
           





        
        
            
        
