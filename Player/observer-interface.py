"""
Represents an interface for player observers.

Meant to be imported and used from observer_interface.py (not observer-interface.py which is included in the
Player directory solely to meet the requirements of Assignment 5). Note that observer_interface.py is a symlink
to observer-interface.py.
"""

from typing import List

from Common.board_state import BoardState
from Common.color import ColorString
from Common.moves import InitialMove, IntermediateMove
from Common.tiles import Tile
from Common.tsuro_types import GameResult


class PlayerObserver:
    """
    Represents an interface for an observer that observes a player as the player plays a game of Tsuro.

    Important note: All of these methods are called (or _not_ called) by the player, so anything shown to the observer
                    could be entirely falsified by the player.
    """

    def set_color(self, color: ColorString) -> None:
        """
        An observer method that is called once at the start of a game to set the color
        that the observed player is playing as

        :param color:   The color that the player is playing as
        """

    def set_players(self, players: List[ColorString]) -> None:
        """
        An observer method that is called once at the start of a game to set the list of players that are
        playing in a given game.

        :param players:     The list of players represented as a list of colors
        """

    def initial_move_offered(self, tiles: List[Tile], board_state: BoardState) -> None:
        """
        An observer method that is called to describe when a player is prompted for an initial move and the data
        that is given to them when they are prompted for an initial move. Note that a call to this method
        is always followed immediately by a call to `initial_move_played`.

        :param tiles:           The list of tiles that the player is allowed to choose between
        :param board_state:     The board state that the player is playing against
        """

    def initial_move_played(
        self, tiles: List[Tile], board_state: BoardState, move: InitialMove
    ) -> None:
        """
        An observer method that is called to describe when a player returns an initial move to be placed. Note that a
        call to this method is always immediately preceded by a call to `initial_move_offered`.

        Note that since move is a move returned by a player, it is not guaranteed to be a valid move.

        :param tiles:           The list of tiles that the player is allowed to choose between
        :param board_state:     The board state that the player is playing against
        :param move:            The initial move that the player placed on the board
        """

    def intermediate_move_offered(
        self, tiles: List[Tile], board_state: BoardState
    ) -> None:
        """
        An observer method that is called to describe when a player is prompted for an intermediate move and the data
        that is given to them when they are prompted for an intermediate move. Note that a call to this method is always
        immediately followed by a call to `intermediate_move_played`.

        Note that since move is a move returned by a player, it is not guaranteed to be a valid move.

        :param tiles:           The list of tiles that the player is allowed to choose between
        :param board_state:     The board state that the player is playing against
        """

    def intermediate_move_played(
        self, tiles: List[Tile], board_state: BoardState, move: IntermediateMove
    ) -> None:
        """
        An observer method that is called to describe when a player returns an intermediate move to be placed. Note
        that a call to this method is always immediately preceded by a call to `intermediate_move_offered`.

        :param tiles:           The list of tiles that the player is allowed to choose between
        :param board_state:     The board state that the player is playing against
        :param move:            The intermediate move that the player placed on the board
        """

    def game_result(self, result: GameResult) -> None:
        """
        An observer method that is called to describe when a player is given the game results after a game of Tsuro
        is completed.

        :param result:  The game results
        """
