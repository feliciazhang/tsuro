"""
A simple deterministic player strategy as described in Assignment 7:
http://www.ccs.neu.edu/home/matthias/4500-f19/7.html

Meant to be imported and used from second_s.py (not second-s.py which is included in the
Player directory solely to meet the requirements of Assignment 7). Note that second_s.py is a symlink
to second-s.py.

In order to implement this strategy, we did not have to change the Player at all.
"""
from typing import List

from Common.board_state import BoardState
from Common.moves import IntermediateMove
from Common.result import Result, error, ok
from Common.rules import EXPECTED_TILE_COUNT_INTERMEDIATE_MOVE
from Common.tiles import Tile
from Common.validation import validate_types
from Player.first_s import FirstS


class SecondS(FirstS):
    """
    Implements a simple deterministic strategy for Tsuro games as described in Assignment 7
    """

    @validate_types
    def generate_move(self, tiles: List[Tile], board_state: BoardState) -> Result[Tile]:
        """
        Try all tiles in all rotations clockwise, returning the first legal tile.
        If no tiles are valid, return the first tile without rotation.

        :param tiles:           The list of tile options
        :param board_state:     The state of the current board
        :return:                A result containing the tile that will be placed for the given player
        """
        if len(tiles) != EXPECTED_TILE_COUNT_INTERMEDIATE_MOVE:
            return error(
                f"Strategy.generate_move given {len(tiles)} (expected {EXPECTED_TILE_COUNT_INTERMEDIATE_MOVE})"
            )

        for tile in tiles:
            for rot_tile in tile.all_rotations():
                r_illegal = self.rule_checker.is_move_illegal(
                    board_state, IntermediateMove(rot_tile, self.color)
                )
                if not r_illegal.is_error() and not r_illegal.value():
                    return ok(rot_tile)

        return ok(tiles[0])
