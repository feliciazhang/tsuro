# pylint: skip-file
from copy import deepcopy

from pyrsistent import pmap

from Common.board import Board
from Common.board_position import BoardPosition
from Common.board_state import BoardState
from Common.moves import InitialMove, IntermediateMove
from Common.rules import RuleChecker
from Common.tiles import Port, index_to_tile


def test_validate_initial_move_allowed() -> None:
    rc = RuleChecker()
    bs = BoardState()

    r = rc.validate_initial_move(
        bs,
        [index_to_tile(1), index_to_tile(2), index_to_tile(3)],
        InitialMove(BoardPosition(2, 0), index_to_tile(2), Port.BottomLeft, "red"),
    )
    assert r.is_ok()
    assert bs == BoardState()  # board state is unchanged

    r = rc.validate_initial_move(
        bs,
        [index_to_tile(1), index_to_tile(2), index_to_tile(3)],
        InitialMove(BoardPosition(0, 2), index_to_tile(2), Port.BottomLeft, "red"),
    )
    assert r.is_ok()
    assert bs == BoardState()  # board state is unchanged

    r = rc.validate_initial_move(
        bs,
        [index_to_tile(2), index_to_tile(3), index_to_tile(4)],
        InitialMove(BoardPosition(9, 2), index_to_tile(2), Port.BottomLeft, "white"),
    )
    assert r.is_ok()
    assert bs == BoardState()  # board state is unchanged


def test_validate_initial_move_not_in_choices() -> None:
    rc = RuleChecker()
    bs = BoardState()

    r = rc.validate_initial_move(
        bs,
        [index_to_tile(1), index_to_tile(3), index_to_tile(4)],
        InitialMove(BoardPosition(0, 2), index_to_tile(2), Port.BottomLeft, "red"),
    )
    assert r.is_error()
    assert (
        r.error()
        == "tile Tile(idx=2, edges=[(0, 5), (1, 4), (2, 7), (3, 6)]) is not in the list of tiles [Tile(idx=1, edges=[(0, 4), (1, 5), (2, 6), (3, 7)]), Tile(idx=3, edges=[(0, 4), (1, 3), (2, 6), (5, 7)]), Tile(idx=4, edges=[(0, 7), (1, 2), (3, 4), (5, 6)])] the player was given"
    )
    assert bs == BoardState()  # board state is unchanged


def test_validate_initial_move_double_play() -> None:
    rc = RuleChecker()
    bs = BoardState()

    bs = bs.with_live_players(
        bs.live_players.set("red", (BoardPosition(5, 0), Port.RightBottom))
    )
    copied = deepcopy(bs)
    r = rc.validate_initial_move(
        copied,
        [index_to_tile(1), index_to_tile(2), index_to_tile(3)],
        InitialMove(BoardPosition(0, 2), index_to_tile(2), Port.BottomLeft, "red"),
    )
    assert r.is_error()
    assert (
        r.error() == "cannot place player red since the player is already on the board"
    )
    assert bs == copied  # board state is unchanged


def test_validate_initial_move_on_top_of() -> None:
    rc = RuleChecker()
    bs = BoardState()

    bs = bs.with_tile(index_to_tile(5), BoardPosition(0, 2))
    r = rc.validate_initial_move(
        bs,
        [index_to_tile(1), index_to_tile(2), index_to_tile(3)],
        InitialMove(BoardPosition(0, 2), index_to_tile(2), Port.BottomLeft, "red"),
    )
    assert r.is_error()
    assert (
        r.error()
        == "cannot place tile at position BoardPosition(x=0, y=2) since there is already a tile at that position"
    )


def test_validate_initial_move_middle() -> None:
    rc = RuleChecker()
    bs = BoardState()

    r = rc.validate_initial_move(
        bs,
        [index_to_tile(1), index_to_tile(2), index_to_tile(3)],
        InitialMove(BoardPosition(2, 3), index_to_tile(2), Port.BottomLeft, "red"),
    )
    assert r.is_error()
    assert (
        r.error()
        == "cannot make an initial move at position BoardPosition(x=2, y=3) since it is not on the edge"
    )


def test_validate_initial_move_facing_edge() -> None:
    rc = RuleChecker()
    bs = BoardState()

    r = rc.validate_initial_move(
        bs,
        [index_to_tile(1), index_to_tile(2), index_to_tile(3)],
        InitialMove(BoardPosition(0, 3), index_to_tile(2), Port.LeftTop, "red"),
    )
    assert r.is_error()
    assert (
        r.error()
        == "cannot make an initial move at position BoardPosition(x=0, y=3), port 7 since it does not face the interior of the board"
    )

    r = rc.validate_initial_move(
        bs,
        [index_to_tile(1), index_to_tile(2), index_to_tile(3)],
        InitialMove(BoardPosition(3, 0), index_to_tile(2), Port.TopRight, "red"),
    )
    assert r.is_error()
    assert (
        r.error()
        == "cannot make an initial move at position BoardPosition(x=3, y=0), port 1 since it does not face the interior of the board"
    )


def test_validate_place_tile_inexistent_player() -> None:
    rc = RuleChecker()
    bs = BoardState()

    r = rc.validate_move(
        bs,
        [index_to_tile(1), index_to_tile(2)],
        IntermediateMove(index_to_tile(1), "red"),
    )
    assert r.is_error()
    assert r.error() == "cannot place a tile for player red since they are not alive"


def test_validate_place_tile_not_in_choices() -> None:
    rc = RuleChecker()
    bs = BoardState()

    bs = bs.with_live_players(
        bs.live_players.set("red", (BoardPosition(2, 0), Port.TopRight))
    )
    r = rc.validate_move(
        bs,
        [index_to_tile(2), index_to_tile(3)],
        IntermediateMove(index_to_tile(1), "red"),
    )
    assert r.is_error()
    assert (
        r.error()
        == "tile Tile(idx=1, edges=[(0, 4), (1, 5), (2, 6), (3, 7)]) is not in the list of tiles [Tile(idx=2, edges=[(0, 5), (1, 4), (2, 7), (3, 6)]), Tile(idx=3, edges=[(0, 4), (1, 3), (2, 6), (5, 7)])] the player was given"
    )


def test_validate_place_tile_unnecessary_suicide() -> None:
    rc = RuleChecker()
    bs = BoardState()

    bs = bs.with_live_players(
        bs.live_players.set("red", (BoardPosition(2, 0), Port.RightTop))
    )
    bs = bs.with_tile(index_to_tile(2), BoardPosition(2, 0))
    r = rc.is_move_suicidal(bs, IntermediateMove(index_to_tile(4), "red"))
    assert r.is_ok()
    assert r.value()
    r = rc.is_move_suicidal(bs, IntermediateMove(index_to_tile(3), "red"))
    assert r.is_ok()
    assert not r.value()
    r2 = rc.validate_move(
        bs,
        [index_to_tile(3), index_to_tile(4)],
        IntermediateMove(index_to_tile(4), "red"),
    )
    assert r2.is_error()
    assert (
        r2.error()
        == "player chose a suicidal move when this does not cause a suicide: Tile(idx=3, edges=[(0, 4), (1, 3), (2, 6), (5, 7)])"
    )


def test_validate_place_tile_required_suicide() -> None:
    rc = RuleChecker()
    bs = BoardState()

    bs = bs.with_live_players(
        bs.live_players.set("red", (BoardPosition(2, 0), Port.RightTop))
    )
    bs = bs.with_tile(index_to_tile(2), BoardPosition(2, 0))
    r = rc.is_move_suicidal(bs, IntermediateMove(index_to_tile(4), "red"))
    assert r.is_ok()
    assert r.value()
    r2 = rc.validate_move(
        bs,
        [index_to_tile(4), index_to_tile(4)],
        IntermediateMove(index_to_tile(4).rotate(), "red"),
    )
    assert r2.is_ok()


def test_validate_place_tile_unnecessary_loop() -> None:
    rc = RuleChecker()
    bs = BoardState()

    bs = bs.with_live_players(
        bs.live_players.set("red", (BoardPosition(2, 0), Port.RightBottom))
    )
    bs = bs.with_tile(index_to_tile(4), BoardPosition(2, 0))
    bs = bs.with_tile(index_to_tile(4), BoardPosition(2, 1))
    bs = bs.with_tile(index_to_tile(4), BoardPosition(3, 1))
    r = rc.move_creates_loop(bs, IntermediateMove(index_to_tile(4), "red"))
    assert r.is_ok()
    assert r.value()
    r = rc.move_creates_loop(bs, IntermediateMove(index_to_tile(5), "red"))
    assert r.is_ok()
    assert r.value()
    r = rc.is_move_suicidal(bs, IntermediateMove(index_to_tile(5).rotate(), "red"))
    assert r.is_ok()
    assert not r.value()

    r2 = rc.validate_move(
        bs,
        [index_to_tile(5), index_to_tile(4)],
        IntermediateMove(index_to_tile(4), "red"),
    )
    assert r2.is_error()
    assert (
        r2.error()
        == "player chose a loopy move when this does not create a loop: Tile(idx=5, edges=[(0, 7), (1, 5), (2, 6), (3, 4)])"
    )


def test_validate_place_tile_forced_loop_or_suicide() -> None:
    rc = RuleChecker()
    bs = BoardState()

    bs = bs.with_live_players(
        bs.live_players.set("red", (BoardPosition(2, 0), Port.RightBottom))
    )
    bs = bs.with_tile(index_to_tile(4), BoardPosition(2, 0))
    bs = bs.with_tile(index_to_tile(4), BoardPosition(2, 1))
    bs = bs.with_tile(index_to_tile(4), BoardPosition(3, 1))
    r = rc.move_creates_loop(bs, IntermediateMove(index_to_tile(4), "red"))
    assert r.is_ok()
    assert r.value()
    r = rc.is_move_suicidal(bs, IntermediateMove(index_to_tile(7), "red"))
    assert r.is_ok()
    assert r.value()

    r2 = rc.validate_move(
        bs,
        [index_to_tile(7), index_to_tile(4)],
        IntermediateMove(index_to_tile(4), "red"),
    )
    assert r2.is_error()
    assert (
        r2.error()
        == "player chose a loopy move when this does not create a loop: Tile(idx=7, edges=[(0, 3), (1, 6), (2, 5), (4, 7)])"
    )

    r3 = rc.validate_move(
        bs,
        [index_to_tile(7), index_to_tile(4)],
        IntermediateMove(index_to_tile(7), "red"),
    )
    assert r3.is_error()
    assert (
        r3.error()
        == "player chose a suicidal move when this does not cause a suicide: Tile(idx=4, edges=[(0, 7), (1, 2), (3, 4), (5, 6)])"
    )


def test_validate_place_tile_required_loop() -> None:
    rc = RuleChecker()
    bs = BoardState()

    bs = bs.with_live_players(
        bs.live_players.set("red", (BoardPosition(2, 0), Port.RightTop))
    )
    bs = bs.with_tile(index_to_tile(4), BoardPosition(2, 0))
    bs = bs.with_tile(index_to_tile(4), BoardPosition(2, 1))
    bs = bs.with_tile(index_to_tile(4), BoardPosition(3, 1))
    r = rc.is_move_suicidal(bs, IntermediateMove(index_to_tile(4), "red"))
    assert r.is_ok()
    assert r.value()

    r2 = rc.validate_move(
        bs,
        [index_to_tile(4), index_to_tile(4)],
        IntermediateMove(index_to_tile(4), "red"),
    )
    assert r2.is_ok()


def test_validate_place_tile_loop_someone_else() -> None:
    rc = RuleChecker()
    bs = BoardState()

    bs = bs.with_live_players(
        bs.live_players.set("red", (BoardPosition(2, 0), Port.RightBottom))
    )
    bs = bs.with_live_players(
        bs.live_players.set("white", (BoardPosition(4, 0), Port.LeftTop))
    )
    bs = bs.with_tile(index_to_tile(4), BoardPosition(2, 0))
    bs = bs.with_tile(index_to_tile(4), BoardPosition(2, 1))
    bs = bs.with_tile(index_to_tile(4), BoardPosition(3, 1))
    bs = bs.with_tile(index_to_tile(2), BoardPosition(4, 0))

    # The move is suicidal for red but not for white
    r = rc.is_move_suicidal(bs, IntermediateMove(index_to_tile(13).rotate(), "white"))
    assert r.is_ok()
    assert not r.value()
    r = rc.move_creates_loop(bs, IntermediateMove(index_to_tile(13).rotate(), "red"))
    assert r.is_ok()
    assert r.value()
    # But it does create a loop no matter who places it
    r = rc.move_creates_loop(bs, IntermediateMove(index_to_tile(13).rotate(), "white"))
    assert r.is_ok()
    assert r.value()
    r = rc.move_creates_loop(bs, IntermediateMove(index_to_tile(13).rotate(), "red"))
    assert r.is_ok()
    assert r.value()
    # And thus it is illegal
    r = rc.is_move_illegal(bs, IntermediateMove(index_to_tile(13).rotate(), "white"))
    assert r.is_ok()
    assert r.value()
    r = rc.is_move_illegal(bs, IntermediateMove(index_to_tile(13).rotate(), "red"))
    assert r.is_ok()
    assert r.value()

    # Red and white are both not allowed to place the move since it causes a loop
    r2 = rc.validate_move(
        bs,
        [index_to_tile(13).rotate().rotate(), index_to_tile(6)],
        IntermediateMove(index_to_tile(13).rotate(), "white"),
    )
    assert r2.is_error()
    assert (
        r2.error()
        == "player chose a loopy move when this does not create a loop: Tile(idx=13, edges=[(0, 7), (1, 2), (3, 5), (4, 6)])"
    )
    r2 = rc.validate_move(
        bs,
        [index_to_tile(13).rotate().rotate(), index_to_tile(6)],
        IntermediateMove(index_to_tile(13).rotate(), "red"),
    )
    assert r2.is_error()
    assert (
        r2.error()
        == "player chose a loopy move when this does not create a loop: Tile(idx=13, edges=[(0, 7), (1, 2), (3, 5), (4, 6)])"
    )


def test_is_move_suicidal_walk_off_edge() -> None:
    rc = RuleChecker()
    bs = BoardState()

    bs = bs.with_live_players(
        bs.live_players.set("red", (BoardPosition(2, 0), Port.RightTop))
    )
    bs = bs.with_tile(index_to_tile(2), BoardPosition(2, 0))
    r = rc.is_move_suicidal(bs, IntermediateMove(index_to_tile(4), "red"))
    assert r.is_ok()
    assert r.value()


def test_is_move_suicidal_loop() -> None:
    rc = RuleChecker()
    bs = BoardState()

    bs = bs.with_live_players(
        bs.live_players.set("red", (BoardPosition(2, 0), Port.RightBottom))
    )
    bs = bs.with_tile(index_to_tile(4), BoardPosition(2, 0))
    bs = bs.with_tile(index_to_tile(4), BoardPosition(2, 1))
    bs = bs.with_tile(index_to_tile(4), BoardPosition(3, 1))
    r = rc.move_creates_loop(bs, IntermediateMove(index_to_tile(4), "red"))
    assert r.is_ok()
    assert r.value()


def test_allow_collision() -> None:
    rc = RuleChecker()
    b = Board()

    move = InitialMove(BoardPosition(0, 0), index_to_tile(4), Port.BottomRight, "red")
    assert rc.validate_initial_move(
        b.get_board_state(),
        [index_to_tile(4), index_to_tile(5), index_to_tile(6)],
        move,
    ).is_ok()
    r = b.initial_move(move)
    assert r.is_ok()
    assert b._board_state.get_tile(BoardPosition(0, 0)) == index_to_tile(4)
    assert b.live_players["red"] == (BoardPosition(0, 0), Port.BottomRight)

    move = InitialMove(BoardPosition(2, 0), index_to_tile(22), Port.LeftBottom, "green")
    assert rc.validate_initial_move(
        b.get_board_state(),
        [index_to_tile(22), index_to_tile(5), index_to_tile(6)],
        move,
    ).is_ok()
    r = b.initial_move(move)
    assert r.is_ok()
    assert b._board_state.get_tile(BoardPosition(2, 0)) == index_to_tile(22)
    assert b.live_players["green"] == (BoardPosition(2, 0), Port.LeftBottom)

    move = InitialMove(BoardPosition(4, 0), index_to_tile(22), Port.LeftBottom, "blue")
    assert rc.validate_initial_move(
        b.get_board_state(),
        [index_to_tile(22), index_to_tile(5), index_to_tile(6)],
        move,
    ).is_ok()
    r = b.initial_move(move)
    assert r.is_ok()
    assert b._board_state.get_tile(BoardPosition(4, 0)) == index_to_tile(22)
    assert b.live_players["blue"] == (BoardPosition(4, 0), Port.LeftBottom)

    move = InitialMove(BoardPosition(6, 0), index_to_tile(22), Port.LeftBottom, "white")
    assert rc.validate_initial_move(
        b.get_board_state(),
        [index_to_tile(22), index_to_tile(5), index_to_tile(6)],
        move,
    ).is_ok()
    r = b.initial_move(move)
    assert r.is_ok()
    assert b._board_state.get_tile(BoardPosition(6, 0)) == index_to_tile(22)
    assert b.live_players["white"] == (BoardPosition(6, 0), Port.LeftBottom)

    move = InitialMove(BoardPosition(8, 0), index_to_tile(22), Port.LeftBottom, "black")
    assert rc.validate_initial_move(
        b.get_board_state(),
        [index_to_tile(22), index_to_tile(5), index_to_tile(6)],
        move,
    ).is_ok()
    r = b.initial_move(move)
    assert r.is_ok()
    assert b._board_state.get_tile(BoardPosition(8, 0)) == index_to_tile(22)
    assert b.live_players["black"] == (BoardPosition(8, 0), Port.LeftBottom)

    intermediate_move = IntermediateMove(index_to_tile(22), "black")
    assert rc.validate_move(
        b.get_board_state(), [index_to_tile(22), index_to_tile(5)], intermediate_move
    ).is_ok()
    r = b.intermediate_move(intermediate_move)
    assert r.is_ok()
    assert b._board_state.get_tile(BoardPosition(7, 0)) == index_to_tile(22)

    intermediate_move = IntermediateMove(index_to_tile(22), "black")
    assert rc.validate_move(
        b.get_board_state(), [index_to_tile(22), index_to_tile(5)], intermediate_move
    ).is_ok()
    r = b.intermediate_move(intermediate_move)
    assert r.is_ok()
    assert b._board_state.get_tile(BoardPosition(5, 0)) == index_to_tile(22)

    intermediate_move = IntermediateMove(index_to_tile(22), "black")
    assert rc.validate_move(
        b.get_board_state(), [index_to_tile(22), index_to_tile(5)], intermediate_move
    ).is_ok()
    r = b.intermediate_move(intermediate_move)
    assert r.is_ok()
    assert b._board_state.get_tile(BoardPosition(3, 0)) == index_to_tile(22)

    intermediate_move = IntermediateMove(index_to_tile(22), "black")
    assert rc.validate_move(
        b.get_board_state(), [index_to_tile(22), index_to_tile(5)], intermediate_move
    ).is_ok()
    r = b.intermediate_move(intermediate_move)
    assert r.is_ok()
    assert b._board_state.get_tile(BoardPosition(1, 0)) == index_to_tile(22)

    assert len(b._board_state.live_players) == 5
    assert len(set(b._board_state.live_players.values())) == 1
    assert b.live_players == pmap(
        {
            "black": (BoardPosition(x=0, y=0), 4),
            "blue": (BoardPosition(x=0, y=0), 4),
            "green": (BoardPosition(x=0, y=0), 4),
            "red": (BoardPosition(x=0, y=0), 4),
            "white": (BoardPosition(x=0, y=0), 4),
        }
    )


def test_place_tile_remove_other_player() -> None:
    # Black kills red by driving them off the edge of the board
    rc = RuleChecker()
    bs = BoardState()

    bs = bs.with_live_players(
        bs.live_players.set("red", (BoardPosition(2, 2), Port.RightBottom))
    )
    bs = bs.with_live_players(
        bs.live_players.set("black", (BoardPosition(4, 2), Port.LeftTop))
    )
    bs = bs.with_tile(index_to_tile(2), BoardPosition(2, 0))
    bs = bs.with_tile(index_to_tile(2), BoardPosition(2, 1))
    bs = bs.with_tile(index_to_tile(3), BoardPosition(2, 2))

    bs = bs.with_tile(index_to_tile(2), BoardPosition(4, 0))
    bs = bs.with_tile(index_to_tile(2), BoardPosition(4, 1))
    bs = bs.with_tile(index_to_tile(32).rotate(), BoardPosition(4, 2))

    r = rc.is_move_suicidal(bs, IntermediateMove(index_to_tile(2), "red"))
    assert r.is_ok()
    assert r.value()
    move = IntermediateMove(index_to_tile(2), "black")
    r = rc.is_move_suicidal(bs, move)
    assert r.is_ok()
    assert not r.value()
    assert rc.validate_move(bs, [index_to_tile(2), index_to_tile(3)], move).is_ok()
    board = Board(bs)
    assert board.intermediate_move(move).is_ok()

    assert "red" not in board.live_players
    assert board.live_players["black"] == (BoardPosition(x=2, y=2), 6)
    bs = bs.with_tile(index_to_tile(2), BoardPosition(4, 2))


def test_is_move_suicidal_inexistent() -> None:
    rc = RuleChecker()
    bs = BoardState()

    r = rc.is_move_suicidal(bs, IntermediateMove(index_to_tile(22), "red"))
    assert r.is_error()
    assert r.error() == "player red is not alive thus the move cannot be suicidal"


def test_wrong_number_tile_choices() -> None:
    rc = RuleChecker()
    bs = BoardState()

    r = rc.validate_initial_move(
        bs,
        [index_to_tile(1)],
        InitialMove(BoardPosition(0, 2), index_to_tile(1), Port.BottomRight, "red"),
    )
    assert r.is_error()
    assert r.error() == "cannot validate move with 1 tile choices (expected 3)"
    r = rc.validate_initial_move(
        bs,
        [index_to_tile(1), index_to_tile(2), index_to_tile(3), index_to_tile(4)],
        InitialMove(BoardPosition(0, 2), index_to_tile(1), Port.BottomRight, "red"),
    )
    assert r.is_error()
    assert r.error() == "cannot validate move with 4 tile choices (expected 3)"

    r = rc.validate_move(
        bs, [index_to_tile(1)], IntermediateMove(index_to_tile(1), "red")
    )
    assert r.is_error()
    assert (
        r.error()
        == "cannot validate move with 1 tile choices (expected 2)"
    )
    r = rc.validate_move(
        bs,
        [index_to_tile(1), index_to_tile(3), index_to_tile(2)],
        IntermediateMove(index_to_tile(1), "red"),
    )
    assert r.is_error()
    assert (
        r.error()
        == "cannot validate move with 3 tile choices (expected 2)"
    )


def test_both_moves_illegal() -> None:
    rc = RuleChecker()
    bs = BoardState()

    bs = bs.with_tile(index_to_tile(4), BoardPosition(2, 1))
    bs = bs.with_tile(index_to_tile(4), BoardPosition(3, 1))
    bs = bs.with_tile(index_to_tile(24), BoardPosition(2, 0))
    bs = bs.with_tile(index_to_tile(22), BoardPosition(4, 0))
    bs = bs.with_live_players(
        bs.live_players.set("red", (BoardPosition(2, 0), Port.RightBottom)).set(
            "white", (BoardPosition(4, 0), Port.LeftBottom)
        )
    )
    move = IntermediateMove(index_to_tile(24), "white")
    r = rc.validate_move(bs, [index_to_tile(24), index_to_tile(24)], move)
    assert r.is_error()
    assert (
        r.error()
        == "player chose a loopy move when this does not create a loop: Tile(idx=24, edges=[(0, 7), (1, 2), (3, 6), (4, 5)])"
    )
