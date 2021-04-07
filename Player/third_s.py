"""
A third deterministic player strategy as described in Assignment 9:
http://www.ccs.neu.edu/home/matthias/4500-f19/9.html

Meant to be imported and used third_s.py (not third-s.py). Note that third_s.py is a symlink
to third-s.py.
"""
from typing import List, Tuple

from Common.board_constraint import PhysicalConstraintChecker
from Common.board_position import (
    MAX_BOARD_COORDINATE,
    MIN_BOARD_COORDINATE,
    BoardPosition,
)
from Common.board_state import BoardState
from Common.result import Result, error, ok
from Common.rules import (
    EXPECTED_TILE_COUNT_INITIAL_MOVE,
    EXPECTED_TILE_COUNT_INTERMEDIATE_MOVE,
)
from Common.moves import IntermediateMove
from Common.tiles import Port, PortID, Tile
from Common.validation import validate_types
from Player.strategy import Strategy


class ThirdS(Strategy):
    # pylint: disable=no-self-use
    """
    Implements a simple deterministic strategy for Tsuro games as described in Assignment 6
    """

    @validate_types
    def generate_first_move(
        self, tiles: List[Tile], board_state: BoardState
    ) -> Result[Tuple[BoardPosition, Tile, PortID]]:
        """
        Generate the first move by choosing from the given list of 3 tiles. Returns the move along with
        the port that the player's token should be placed on. `set_color` and `set_rule_checker` will
        be called prior to this method.

        This strategy just chooses the first valid move checking positions counter-clockwise from (0,0)
        exclusive and checking ports counter-clockwise from top left.

        :param tiles:           The set of tile options for the first move
        :param board_state:     The state of the current board
        :return:                A result containing a tuple containing the board position, tile, and port ID
                                for the player's initial move
        """
        tile = tiles[2]

        move = self._first_legal_posn_on_vertical_side(MIN_BOARD_COORDINATE,
            range(MIN_BOARD_COORDINATE + 1, MAX_BOARD_COORDINATE), board_state, tile)
        if not move:
            move = self._first_legal_posn_on_horizontal_side(MAX_BOARD_COORDINATE,
                range(MIN_BOARD_COORDINATE, MAX_BOARD_COORDINATE + 1), board_state, tile)
        if not move:
            move = self._first_legal_posn_on_vertical_side(MAX_BOARD_COORDINATE,
                reversed(range(MIN_BOARD_COORDINATE, MAX_BOARD_COORDINATE)), board_state, tile)
        if not move:
            move = self._first_legal_posn_on_horizontal_side(MIN_BOARD_COORDINATE,
                reversed(range(MIN_BOARD_COORDINATE + 1, MAX_BOARD_COORDINATE)), board_state, tile)

        if move:
            return ok(move)
        else:
            return error("Failed to find a valid initial move!")

    @validate_types
    def _first_legal_posn_on_vertical_side(self,
        x: int, posn_range_y, board_state: BoardState, tile: Tile):
        """
        Generate the first move with the given tile and board state for a vertical column of possible
        tile position as defined by the given x coordinate and range of y coordinate values that is legal

        :param tile:            The tile to place
        :param board_state:     The state of the current board
        :param x:               The x coordinate of the column
        :param posn_range_y:    The range of y coordinates to try in order
        :return:                A result containing a tuple containing the board position, tile, and port ID
                                for the player's initial move
        """
        for y in posn_range_y:
            r_move = self._find_valid_move(board_state, BoardPosition(x, y))
            if r_move.is_ok():
                pos, port = r_move.value()
                return (pos, tile, port)

    @validate_types
    def _first_legal_posn_on_horizontal_side(self,
        y: int, posn_range_x, board_state: BoardState, tile:Tile):
        """
        Generate the first move with the given tile and board state for a horizontal row of possible
        tile position as defined by the given y coordinate and range of x coordinate values that is legal

        :param tile:            The tile to place
        :param board_state:     The state of the current board
        :param y:               The y coordinate of the row
        :param posn_range_x:    The range of x coordinates to try in order
        :return:                A result containing a tuple containing the board position, tile, and port ID
                                for the player's initial move
        """
        for x in posn_range_x:
            r_move = self._find_valid_move(board_state, BoardPosition(x, y))
            if r_move.is_ok():
                pos, port = r_move.value()
                return (pos, tile, port)


    @validate_types
    def _find_valid_move(
        self, board_state: BoardState, pos: BoardPosition
    ) -> Result[Tuple[BoardPosition, PortID]]:
        """
        Find a valid move on the board state at the given position

        :param board_state:     The board state to apply the move to
        :param pos:             The position for the move
        :return:                A result containing the position and port or an error if there is no valid move at
                                the given position
        """
        r = PhysicalConstraintChecker.is_valid_initial_position(board_state, pos)
        if r.is_error():
            return error(r.error())
        r_port = self._find_valid_port(board_state, pos)
        if r_port.is_error():
            return error(r_port.error())
        return ok((pos, r_port.value()))

    @validate_types
    def _find_valid_port(
        self, board_state: BoardState, pos: BoardPosition
    ) -> Result[PortID]:
        """
        Find the first port on the board state for a move at the given position going counter-clockwise

        :param board_state:     The board state to apply the move to
        :param pos:             The position for the move
        :return:                A result containing the port or an error if there is no valid port to play on at the
                                given position
        """
        ports = [Port.TopLeft]
        ports.extend(reversed(Port.all()))
        ports = ports[:8]

        for port in ports:
            if PhysicalConstraintChecker.is_valid_initial_port(
                board_state, pos, port
            ).is_ok():
                return ok(port)
        return error("No valid ports on given tile.")

    @validate_types
    def generate_move(self, tiles: List[Tile], board_state: BoardState) -> Result[Tile]:
        """
        Try all tiles in all rotations clockwise starting with the second tile then the first, returning the first legal tile.
        If no tiles orientations are valid, return the second tile without rotation.

        :param tiles:           The list of 2 tile options
        :param board_state:     The state of the current board
        :return:                A result containing the tile that will be placed for the given player
        """
        for tile in reversed(tiles):
            for rot_tile in tile.all_rotations():
                r_illegal = self.rule_checker.is_move_illegal(
                    board_state, IntermediateMove(rot_tile, self.color)
                )
                if not r_illegal.is_error() and not r_illegal.value():
                    return ok(rot_tile)

        return ok(tiles[1])
