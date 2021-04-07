"""
A simple deterministic player strategy as described in Assignment 6:
http://www.ccs.neu.edu/home/matthias/4500-f19/6.html

Meant to be imported and used from first_s.py (not first-s.py which is included in the
Player directory solely to meet the requirements of Assignment 6). Note that first_s.py is a symlink
to first-s.py.
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
from Common.tiles import Port, PortID, Tile
from Common.validation import validate_types
from Player.strategy import Strategy


class FirstS(Strategy):
    # pylint: disable=no-self-use
    """
    Implements a simple deterministic strategy for Tsuro games as described in Assignment 6
    """

    @validate_types
    def generate_first_move(
        self, tiles: List[Tile], board_state: BoardState
    ) -> Result[Tuple[BoardPosition, Tile, PortID]]:
        """
        Generate the first move by choosing from the given list of tiles. Returns the move along with
        the port that the player's token should be placed on. `set_color` and `set_rule_checker` will
        be called prior to this method.

        This strategy just chooses the first valid move checking positions clockwise starting from (1,0)
        and checking ports clockwise from top left.

        :param tiles:           The set of tile options for the first move
        :param board_state:     The state of the current board
        :return:                A result containing a tuple containing the board position, tile, and port ID
                                for the player's initial move
        """
        if len(tiles) != EXPECTED_TILE_COUNT_INITIAL_MOVE:
            return error(
                f"Strategy.generate_first_move given {len(tiles)} (expected {EXPECTED_TILE_COUNT_INITIAL_MOVE})"
            )

        tile = tiles[2]

        # Check the top of the board (exclusive of 0,0) for valid positions
        y = MIN_BOARD_COORDINATE
        for x in range(MIN_BOARD_COORDINATE + 1, MAX_BOARD_COORDINATE + 1):
            r_move = self._find_valid_move(board_state, BoardPosition(x, y))
            if r_move.is_ok():
                pos, port = r_move.value()
                return ok((pos, tile, port))

        # Check the right side of the board for valid positions
        x = MAX_BOARD_COORDINATE
        for y in range(MIN_BOARD_COORDINATE, MAX_BOARD_COORDINATE + 1):
            r_move = self._find_valid_move(board_state, BoardPosition(x, y))
            if r_move.is_ok():
                pos, port = r_move.value()
                return ok((pos, tile, port))

        # Check the bottom of the board for valid positions
        y = MAX_BOARD_COORDINATE
        for x in reversed(range(MIN_BOARD_COORDINATE, MAX_BOARD_COORDINATE + 1)):
            r_move = self._find_valid_move(board_state, BoardPosition(x, y))
            if r_move.is_ok():
                pos, port = r_move.value()
                return ok((pos, tile, port))

        # Check the left side of the board for valid positions (inclusive of 0,0)
        x = MIN_BOARD_COORDINATE
        for y in reversed(range(MIN_BOARD_COORDINATE, MAX_BOARD_COORDINATE + 1)):
            r_move = self._find_valid_move(board_state, BoardPosition(x, y))
            if r_move.is_ok():
                pos, port = r_move.value()
                return ok((pos, tile, port))

        # No move found
        return error("Failed to find a valid initial move!")

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
        Find a valid port on the board state for a move at the given position

        :param board_state:     The board state to apply the move to
        :param pos:             The position for the move
        :return:                A result containing the port or an error if there is no valid port to play on at the
                                given position
        """
        for port in Port.all():
            if PhysicalConstraintChecker.is_valid_initial_port(
                board_state, pos, port
            ).is_ok():
                return ok(port)
        return error("No valid ports on given tile.")

    @validate_types
    def generate_move(self, tiles: List[Tile], board_state: BoardState) -> Result[Tile]:
        """
        Always choose the first tile without rotation.

        :param tiles:           The set of tile options for the first move
        :param board_state:     The state of the current board
        :return:                A result containing the tile that will be placed for the given player
        """
        if len(tiles) != EXPECTED_TILE_COUNT_INTERMEDIATE_MOVE:
            return error(
                f"Strategy.generate_move given {len(tiles)} (expected {EXPECTED_TILE_COUNT_INTERMEDIATE_MOVE})"
            )

        return ok(tiles[0])
