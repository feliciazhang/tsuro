# pylint: skip-file

import random
import time
from typing import Any, cast
from unittest import mock

import pytest

from Common.board import Board
from Common.board_position import BoardPosition
from Common.board_state import BoardState
from Common.moves import InitialMove, IntermediateMove
from Common.tiles import Port, Tile, index_to_tile
from Common.tsuro_types import TileIndex
from Player.player_observer import GraphicalPlayerObserver

TEST_RUN_MOVES = [
    InitialMove(BoardPosition(5, 0), index_to_tile(5), Port.BottomLeft, "red"),
    InitialMove(BoardPosition(2, 0), index_to_tile(3), Port.BottomLeft, "blue"),
    InitialMove(BoardPosition(9, 2), index_to_tile(3), Port.TopRight, "green"),
    IntermediateMove(index_to_tile(2), "red"),
    IntermediateMove(index_to_tile(2), "red"),
    IntermediateMove(index_to_tile(2), "red"),
    IntermediateMove(index_to_tile(4), "green"),
    IntermediateMove(index_to_tile(2), "red"),
    IntermediateMove(index_to_tile(2), "red"),
]


def rand_tile() -> Tile:
    return index_to_tile(cast(TileIndex, random.randint(0, 34)))


@pytest.mark.skip(  # type: ignore
    reason="Meant to be run manually for testing purposes. Displays an animated GraphicalPlayerObserver output to the user."
    "Run manually via: `python3.6 -m Player.player_observer_test`"
)
def test_run() -> None:
    """
    Test function to run the graphical player observer locally with some test data. Meant to be run
    locally and inspected in order to ensure the GUI is working properly.
    :return:    None
    """

    gpo = GraphicalPlayerObserver()
    gpo.set_color("red")
    gpo.set_players(["red", "blue", "green", "black", "white"])

    b = Board()

    for move in TEST_RUN_MOVES:
        if isinstance(move, InitialMove):
            tile_choices = [move.tile, rand_tile(), rand_tile()]
            if move.player == "red":
                gpo.initial_move_offered(tile_choices, b.get_board_state())
            time.sleep(0.5)
            if move.player == "red":
                gpo.initial_move_played(tile_choices, b.get_board_state(), move)
            b.initial_move(move).assert_value()
        elif isinstance(move, IntermediateMove):
            tile_choices = [move.tile, rand_tile()]
            if move.player == "red":
                gpo.intermediate_move_offered(tile_choices, b.get_board_state())
            time.sleep(0.5)
            if move.player == "red":
                gpo.intermediate_move_played(tile_choices, b.get_board_state(), move)
            b.intermediate_move(move).assert_value()
        time.sleep(0.5)


@mock.patch("Player.player_observer.start_websocket_distributor")
@mock.patch("Player.player_observer.subprocess")
@mock.patch("Player.player_observer_test.time")
def test_run_no_chrome(*_: Any) -> None:
    # Just checks that a decently complex play through runs without crashing. Mocks out subprocess
    # so that google-chrome isn't opened. Mocks out time.sleep so that it runs quickly. Mocks out
    # start_websocket_distributor so that it doesn't start another process.
    test_run()


@mock.patch("Player.player_observer.subprocess")
@mock.patch("Player.player_observer.start_websocket_distributor")
def test_ignore_invalid_moves(*_: Any) -> None:
    # Test that giving invalid moves to the observer doesn't crash anything. Mocks out subprocess
    # so that google-chrome isn't opened. Mocks out start_websocket_distributor so that it doesn't
    # start another process.
    b = Board()

    gpo = GraphicalPlayerObserver()
    gpo.set_color("red")
    gpo.set_players(["red", "blue", "green", "black", "white"])

    tile_choices = [index_to_tile(2), index_to_tile(3)]
    gpo.initial_move_played(
        tile_choices,
        b.get_board_state(),
        InitialMove(BoardPosition(2, 3), index_to_tile(2), Port.TopLeft, "red"),
    )

    tile_choices = [index_to_tile(2), index_to_tile(3), index_to_tile(4)]
    gpo.intermediate_move_played(
        tile_choices, b.get_board_state(), IntermediateMove(index_to_tile(2), "red")
    )


if __name__ == "__main__":
    test_run()
