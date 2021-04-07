# pylint: skip-file
from copy import deepcopy

from Common.board_position import BoardPosition
from Common.board_state import BoardState
from Common.tiles import Port, make_tiles, index_to_tile
from Common.board import Board
from Common.moves import IntermediateMove, InitialMove

def test_board_state_get_tile() -> None:
    b = BoardState()
    assert b.get_tile(BoardPosition(x=4, y=3)) is None
    t = make_tiles()[0]
    b_new = b.with_tile(t, BoardPosition(4, 3))
    assert b.get_tile(BoardPosition(x=4, y=3)) is None
    assert b_new.get_tile(BoardPosition(x=4, y=3)) == t


def test_board_state_get_position_of_player() -> None:
    b = BoardState()
    assert b.get_position_of_player("red").is_error()
    t = make_tiles()[0]
    b = b.with_tile(t, BoardPosition(7, 3))
    assert b.get_position_of_player("red").is_error()
    b = b.with_live_players(
        b.live_players.set("red", (BoardPosition(7, 3), Port.BottomRight))
    )
    r = b.get_position_of_player("red")
    assert r.is_ok()
    assert r.value() == (BoardPosition(7, 3), Port.BottomRight)


def test_calculate_adjacent_position_of_player_off_board() -> None:
    b = BoardState()
    t = make_tiles()[0]

    # Facing the top edge
    b = b.with_tile(t, BoardPosition(5, 0))
    b = b.with_live_players(
        b.live_players.set("red", (BoardPosition(5, 0), Port.TopLeft))
    )
    r2 = b.get_position_of_player("red")
    assert r2.is_ok()
    assert r2.value() == (BoardPosition(5, 0), Port.TopLeft)
    r = b.calculate_adjacent_position_of_player("red")
    assert r.is_ok()
    assert r.value() is None

    # Facing the right edge
    b = b.with_tile(t, BoardPosition(9, 5))
    b = b.with_live_players(
        b.live_players.set("red", (BoardPosition(9, 5), Port.RightTop))
    )
    r2 = b.get_position_of_player("red")
    assert r2.is_ok()
    assert r2.value() == (BoardPosition(9, 5), Port.RightTop)
    r = b.calculate_adjacent_position_of_player("red")
    assert r.is_ok()
    assert r.value() is None

    # Facing the bottom edge
    b = b.with_tile(t, BoardPosition(5, 9))
    b = b.with_live_players(
        b.live_players.set("red", (BoardPosition(5, 9), Port.BottomRight))
    )
    r2 = b.get_position_of_player("red")
    assert r2.is_ok()
    assert r2.value() == (BoardPosition(5, 9), Port.BottomRight)
    r = b.calculate_adjacent_position_of_player("red")
    assert r.is_ok()
    assert r.value() is None

    # Facing the left edge
    b = b.with_tile(t, BoardPosition(0, 5))
    b = b.with_live_players(
        b.live_players.set("red", (BoardPosition(0, 5), Port.LeftTop))
    )
    r2 = b.get_position_of_player("red")
    assert r2.is_ok()
    assert r2.value() == (BoardPosition(0, 5), Port.LeftTop)
    r = b.calculate_adjacent_position_of_player("red")
    assert r.is_ok()
    assert r.value() is None


def test_calculate_adjacent_position_of_player_exists() -> None:
    b = BoardState()
    r = b.calculate_adjacent_position_of_player("red")
    assert r.is_error()
    assert r.error() == "player red is not a live player"

    t = make_tiles()[0]
    b = b.with_tile(t, BoardPosition(7, 3))
    b = b.with_live_players(
        b.live_players.set("red", (BoardPosition(7, 3), Port.TopRight))
    )
    r2 = b.get_position_of_player("red")
    assert r2.is_ok()
    assert r2.value() == (BoardPosition(7, 3), Port.TopRight)

    # Facing up
    r3 = b.calculate_adjacent_position_of_player("red")
    assert r3.is_ok()
    assert r3.value() == BoardPosition(7, 2)

    # Facing right
    b = b.with_live_players(
        b.live_players.set("red", (BoardPosition(7, 3), Port.RightBottom))
    )
    r4 = b.calculate_adjacent_position_of_player("red")
    assert r4.is_ok()
    assert r4.value() == BoardPosition(8, 3)

    # Facing down
    b = b.with_live_players(
        b.live_players.set("red", (BoardPosition(7, 3), Port.BottomLeft))
    )
    r5 = b.calculate_adjacent_position_of_player("red")
    assert r5.is_ok()
    assert r5.value() == BoardPosition(7, 4)

    # Facing left
    b = b.with_live_players(
        b.live_players.set("red", (BoardPosition(7, 3), Port.LeftBottom))
    )
    r6 = b.calculate_adjacent_position_of_player("red")
    assert r6.is_ok()
    assert r6.value() == BoardPosition(6, 3)


def test_board_state_copy_eq_hash() -> None:
    b = BoardState()
    t1 = make_tiles()[0]
    b = b.with_tile(t1, BoardPosition(7, 3))
    b = b.with_live_players(
        b.live_players.set("red", (BoardPosition(7, 3), Port.BottomRight))
    )
    t2 = make_tiles()[0]
    b = b.with_tile(t2, BoardPosition(2, 1))
    b = b.with_live_players(
        b.live_players.set("red", (BoardPosition(2, 1), Port.TopLeft))
    )

    assert b == b
    assert b != {}
    assert hash(b) == hash(b)

    copied = deepcopy(b)
    assert copied == b
    assert hash(copied) == hash(b)

def test_to_state_pats() -> None:
    board = Board()
    t1 = index_to_tile(1)
    t2 = index_to_tile(2)
    t3 = index_to_tile(3)

    board.initial_move(InitialMove(BoardPosition(3, 0), t3, Port.BottomRight, "red"))
    board.intermediate_move(IntermediateMove(t2, "red"))
    board.intermediate_move(IntermediateMove(t1, "red"))

    b = board.get_board_state()
    
    assert b.to_state_pats() == [[[1, 0], "red", "F", 3, 2], [[3, 0], 3, 0], [[2, 0], 3, 1]]


