# pylint: skip-file
import pytest

from Common.board import Board
from Common.board_constraint import PhysicalConstraintChecker
from Common.board_position import BoardPosition
from Common.board_state import BoardState
from Common.tiles import Port, index_to_tile


def test_is_valid_initial_port() -> None:
    b = Board()

    # Test that it checks what direction a port is facing
    r = PhysicalConstraintChecker.is_valid_initial_port(
        b._board_state, BoardPosition(0, 5), Port.LeftTop
    )
    assert r.is_error()
    assert (
        r.error()
        == "cannot make an initial move at position BoardPosition(x=0, y=5), port 7 since it does not face the interior of the board"
    )

    r = PhysicalConstraintChecker.is_valid_initial_port(
        b._board_state, BoardPosition(0, 5), Port.LeftBottom
    )
    assert r.is_error()
    assert (
        r.error()
        == "cannot make an initial move at position BoardPosition(x=0, y=5), port 6 since it does not face the interior of the board"
    )

    assert PhysicalConstraintChecker.is_valid_initial_port(
        b._board_state, BoardPosition(0, 5), Port.RightTop
    ).is_ok()

    r = PhysicalConstraintChecker.is_valid_initial_port(
        b._board_state, BoardPosition(5, 0), Port.TopLeft
    )
    assert r.is_error()
    assert (
        r.error()
        == "cannot make an initial move at position BoardPosition(x=5, y=0), port 0 since it does not face the interior of the board"
    )

    r = PhysicalConstraintChecker.is_valid_initial_port(
        b._board_state, BoardPosition(5, 0), Port.TopRight
    )
    assert r.is_error()
    assert (
        r.error()
        == "cannot make an initial move at position BoardPosition(x=5, y=0), port 1 since it does not face the interior of the board"
    )

    assert PhysicalConstraintChecker.is_valid_initial_port(
        b._board_state, BoardPosition(5, 0), Port.RightTop
    ).is_ok()

    # Test that it also checks position just in case
    assert b.place_tile_at_index_with_scissors(
        index_to_tile(2), BoardPosition(0, 5)
    ).is_ok()
    r = PhysicalConstraintChecker.is_valid_initial_port(
        b._board_state, BoardPosition(0, 5), Port.TopRight
    )
    assert r.is_error()
    assert (
        r.error()
        == "cannot place tile at position BoardPosition(x=0, y=5) since there is already a tile at that position"
    )

    r = PhysicalConstraintChecker.is_valid_initial_port(
        b._board_state, BoardPosition(3, 5), Port.TopRight
    )
    assert r.is_error()
    assert (
        r.error()
        == "cannot make an initial move at position BoardPosition(x=3, y=5) since it is not on the edge"
    )

    r = PhysicalConstraintChecker.is_valid_initial_port(
        b._board_state, BoardPosition(0, 6), Port.TopRight
    )
    assert r.is_error()
    assert (
        r.error()
        == "cannot make an initial move at position BoardPosition(x=0, y=6) since the surrounding tiles are not all empty"
    )

    r = PhysicalConstraintChecker.is_valid_initial_port(
        b._board_state, BoardPosition(0, 4), Port.TopRight
    )
    assert r.is_error()
    assert (
        r.error()
        == "cannot make an initial move at position BoardPosition(x=0, y=4) since the surrounding tiles are not all empty"
    )


def test_is_valid_initial_port_corner() -> None:
    b = Board()
    r = PhysicalConstraintChecker.is_valid_initial_port(
        b._board_state, BoardPosition(0, 0), Port.TopLeft
    )
    assert r.is_error()
    assert (
        r.error()
        == "cannot make an initial move at position BoardPosition(x=0, y=0), port 0 since it does not face the interior of the board"
    )

    r = PhysicalConstraintChecker.is_valid_initial_port(
        b._board_state, BoardPosition(0, 0), Port.TopRight
    )
    assert r.is_error()
    assert (
        r.error()
        == "cannot make an initial move at position BoardPosition(x=0, y=0), port 1 since it does not face the interior of the board"
    )

    assert PhysicalConstraintChecker.is_valid_initial_port(
        b._board_state, BoardPosition(0, 0), Port.RightTop
    ).is_ok()
    assert PhysicalConstraintChecker.is_valid_initial_port(
        b._board_state, BoardPosition(0, 0), Port.RightBottom
    ).is_ok()
    assert PhysicalConstraintChecker.is_valid_initial_port(
        b._board_state, BoardPosition(0, 0), Port.BottomRight
    ).is_ok()
    assert PhysicalConstraintChecker.is_valid_initial_port(
        b._board_state, BoardPosition(0, 0), Port.BottomLeft
    ).is_ok()

    r = PhysicalConstraintChecker.is_valid_initial_port(
        b._board_state, BoardPosition(0, 0), Port.LeftBottom
    )
    assert r.is_error()
    assert (
        r.error()
        == "cannot make an initial move at position BoardPosition(x=0, y=0), port 6 since it does not face the interior of the board"
    )

    r = PhysicalConstraintChecker.is_valid_initial_port(
        b._board_state, BoardPosition(0, 0), Port.LeftTop
    )
    assert r.is_error()
    assert (
        r.error()
        == "cannot make an initial move at position BoardPosition(x=0, y=0), port 7 since it does not face the interior of the board"
    )


def test_is_valid_initial_position() -> None:
    b = Board()
    assert b.place_tile_at_index_with_scissors(
        index_to_tile(2), BoardPosition(0, 5)
    ).is_ok()
    assert (
        PhysicalConstraintChecker.is_valid_initial_port(
            b._board_state, BoardPosition(0, 5), Port.TopRight
        ).error()
        == "cannot place tile at position BoardPosition(x=0, y=5) since there is already a tile at that position"
    )
    assert (
        PhysicalConstraintChecker.is_valid_initial_port(
            b._board_state, BoardPosition(3, 5), Port.TopRight
        ).error()
        == "cannot make an initial move at position BoardPosition(x=3, y=5) since it is not on the edge"
    )
    assert (
        PhysicalConstraintChecker.is_valid_initial_port(
            b._board_state, BoardPosition(0, 6), Port.TopRight
        ).error()
        == "cannot make an initial move at position BoardPosition(x=0, y=6) since the surrounding tiles are not all empty"
    )
    assert (
        PhysicalConstraintChecker.is_valid_initial_port(
            b._board_state, BoardPosition(0, 4), Port.TopRight
        ).error()
        == "cannot make an initial move at position BoardPosition(x=0, y=4) since the surrounding tiles are not all empty"
    )
