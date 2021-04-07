from typing import List, Tuple

from Common.board_position import BoardPosition
from Common.board_state import BoardState
from Common.color import ColorString
from Common.json_stream import send_from_conn, rcv_from_conn, close_conn
from Common.player_interface import PlayerInterface
from Common.result import Result, ok
from Common.tiles import PortID, Tile, tile_to_index, tile_pattern_to_tile, network_port_id_to_port_id

# a function that takes in any number of arguments and returns None
nop = lambda *a, **k: None

class RemotePlayer(PlayerInterface):
    """
    A module to represent a remote Tsuro player, handling all communication between referees and the player on the client via a TCP connection. See ../Planning/remote.md for how the remote proxy pattern works. See https://felleisen.org/matthias/4500-f19/10.html for the format of all messages sent and received.

    Connections are closed when the tournament is over or if the TCP connection errors out.
    """
    def __init__(self, connection) -> None:
        self._connection = connection

    def _handle_communication(self, message, handle_received_func) -> Result:
        """
        Send the given message to the RemoteAdmin and handles the received response
        with the given handler function.

        :param message:                 The message to send
        :param handle_received_func:    The function that handles the received message.  
        """
        send_from_conn(self._connection, message)
        r_message = rcv_from_conn(self._connection)
        if r_message.is_ok():
            return handle_received_func(r_message.value())
        else:
            close_conn(self._connection)
            return r_message


    def set_color(self, color: ColorString) -> None:
        """
        Set the color of this Player and send a `playing-as` message to the player.

        :param color: The ColorString assigned to this player.
        """
        message = ["playing-as", [color]]
        self._handle_communication(message, nop)
       
    def set_players(self, players: List[ColorString]) -> None:
        """
        Set the list of other players playing in the Tsuro game

        :param players:     The list of players represented as a list of colors
        """
        message = ["others", players]
        self._handle_communication(message, nop)

    def _handle_initial_received(self, initial: List) -> Result[Tuple[BoardPosition, Tile, PortID]]:
        """
        Returns the initial placement given the initial message.
        """
        board_posn = BoardPosition(initial[2], initial[3])
        tile = tile_pattern_to_tile(initial[0][0], initial[0][1])
        port = network_port_id_to_port_id(initial[1])
        return ok((board_posn, tile, port))

    def generate_first_move(
        self, tiles: List[Tile], board_state: BoardState
    ) -> Result[Tuple[BoardPosition, Tile, PortID]]:
        """
        Send the board state and tile options to the client player via TCP, and receives the initial action
        taken by the player.

        :param tiles:           The set of tile options for the first move
        :param board_state:     The state of the current board
        :return:                A result containing a tuple containing the board position, tile, and port ID
                                for the player's initial move
        """
        state_pats = board_state.to_state_pats()
        message = ["initial", [state_pats, tile_to_index(tiles[0]), tile_to_index(tiles[1]), tile_to_index(tiles[2])]]
        return self._handle_communication(message, self._handle_initial_received)

    def _handle_intermediate_received(self, intermediate: List) -> Result[Tile]:
        """
        Returns an intermediate placement based on the given intermediate message.
        """
        tile = tile_pattern_to_tile(intermediate[0], intermediate[1])
        return ok(tile)

    def generate_move(self, tiles: List[Tile], board_state: BoardState) -> Result[Tile]:
        """
        Send the board state and tile options to the client player via TCP, and receives the action
        taken by the player.

        :param tiles:           The set of tile options for the first move
        :param board_state:     The state of the current board
        :return:                A result containing the tile that will be placed for the given player
        """        
        state_pats = board_state.to_state_pats()
        message = ["take-turn", [state_pats, tile_to_index(tiles[0]), tile_to_index(tiles[1])]]
        return self._handle_communication(message, self._handle_intermediate_received)


    def notify_won_tournament(self, won: bool) -> None:
        """
        Notify the player that their results in a tournament that they participated in

        :param bool:        Whether the player won the tournament
        """
        message = ["end-of-tournament", [won]]
        send_from_conn(self._connection, message)
        rcv_from_conn(self._connection)
        close_conn(self._connection)
