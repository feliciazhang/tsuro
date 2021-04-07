# pylint: skip-file
from typing import List, Tuple, cast

from Common.board import Board
from Common.board_position import BoardPosition
from Common.board_state import BoardState
from Common.color import AllColors
from Common.moves import InitialMove
from Common.rules import RuleChecker
from Common.tiles import Port, PortID, Tile, index_to_tile
from Player.third_s import ThirdS


def test_generate_first_move_0_1() -> None:
    # The first move is just placing a tile at 0,1
    third_s = ThirdS()
    bs = BoardState()

    r = third_s.generate_first_move(
        [index_to_tile(22), index_to_tile(23), index_to_tile(24)], bs
    )
    assert r.assert_value() == (
        BoardPosition(x=0, y=1),
        index_to_tile(24),
        Port.TopLeft,
    )

def test_generate_first_move_0_5() -> None:
    # The first move is placing a tile at 5,0 since there are tiles blocking the other positions
    third_s = ThirdS()
    bs = BoardState()

    bs = bs.with_tile(index_to_tile(0), BoardPosition(0, 1))
    bs = bs.with_tile(index_to_tile(0), BoardPosition(0, 3))
    bs = bs.with_tile(index_to_tile(1), BoardPosition(0, 5))

    r = third_s.generate_first_move(
        [index_to_tile(22), index_to_tile(23), index_to_tile(3)], bs
    )
    assert r.assert_value() == (
        BoardPosition(x=0, y=7),
        index_to_tile(3),
        Port.TopLeft,
    )


def test_generate_first_move_0_9() -> None:
    # The first move is placing a tile at 9,0 since there are tiles blocking the other positions
    third_s = ThirdS()
    bs = BoardState()

    bs = bs.with_tile(index_to_tile(0), BoardPosition(0, 1))
    bs = bs.with_tile(index_to_tile(0), BoardPosition(0, 3))
    bs = bs.with_tile(index_to_tile(1), BoardPosition(0, 5))
    bs = bs.with_tile(index_to_tile(3), BoardPosition(0, 7))

    r = third_s.generate_first_move(
        [index_to_tile(22), index_to_tile(23), index_to_tile(4)], bs
    )
    assert r.assert_value() == (
        BoardPosition(x=0, y=9),
        index_to_tile(4),
        Port.TopLeft,
    )


def test_generate_first_move_2_9() -> None:
    # The first move is placing a tile at 9,2 since there are tiles blocking the other positions
    third_s = ThirdS()
    bs = BoardState()

    bs = bs.with_tile(index_to_tile(0), BoardPosition(0, 1))
    bs = bs.with_tile(index_to_tile(0), BoardPosition(0, 3))
    bs = bs.with_tile(index_to_tile(1), BoardPosition(0, 5))
    bs = bs.with_tile(index_to_tile(3), BoardPosition(0, 7))
    bs = bs.with_tile(index_to_tile(4), BoardPosition(0, 9))

    r = third_s.generate_first_move(
        [index_to_tile(22), index_to_tile(23), index_to_tile(4)], bs
    )
    assert r.assert_value() == (BoardPosition(x=2, y=9), index_to_tile(4), Port.TopLeft)


def test_generate_first_move_9_9() -> None:
    # The first move is placing a tile at 9,8 since there are tiles blocking the other positions
    third_s = ThirdS()
    bs = BoardState()

    bs = bs.with_tile(index_to_tile(0), BoardPosition(0, 1))
    bs = bs.with_tile(index_to_tile(0), BoardPosition(0, 3))
    bs = bs.with_tile(index_to_tile(1), BoardPosition(0, 5))
    bs = bs.with_tile(index_to_tile(3), BoardPosition(0, 7))
    bs = bs.with_tile(index_to_tile(4), BoardPosition(0, 9))
    bs = bs.with_tile(index_to_tile(5), BoardPosition(2, 9))
    bs = bs.with_tile(index_to_tile(6), BoardPosition(4, 9))
    bs = bs.with_tile(index_to_tile(7), BoardPosition(7, 9))

    r = third_s.generate_first_move(
        [index_to_tile(22), index_to_tile(23), index_to_tile(4)], bs
    )
    assert r.assert_value() == (BoardPosition(x=9, y=9), index_to_tile(4), Port.TopLeft)


def test_generate_first_move_8_0() -> None:
    # The first move is placing a tile at 8,9 since there are tiles blocking the other positions
    third_s = ThirdS()
    bs = BoardState()

    bs = bs.with_tile(index_to_tile(0), BoardPosition(0, 1))
    bs = bs.with_tile(index_to_tile(0), BoardPosition(0, 3))
    bs = bs.with_tile(index_to_tile(1), BoardPosition(0, 5))
    bs = bs.with_tile(index_to_tile(3), BoardPosition(0, 7))
    bs = bs.with_tile(index_to_tile(4), BoardPosition(0, 9))
    bs = bs.with_tile(index_to_tile(5), BoardPosition(2, 9))
    bs = bs.with_tile(index_to_tile(6), BoardPosition(4, 9))
    bs = bs.with_tile(index_to_tile(7), BoardPosition(7, 9))
    bs = bs.with_tile(index_to_tile(8), BoardPosition(9, 9))
    bs = bs.with_tile(index_to_tile(6), BoardPosition(9, 6))
    bs = bs.with_tile(index_to_tile(7), BoardPosition(9, 3))
    bs = bs.with_tile(index_to_tile(8), BoardPosition(9, 1))

    r = third_s.generate_first_move(
        [index_to_tile(22), index_to_tile(23), index_to_tile(4)], bs
    )
    assert r.assert_value() == (BoardPosition(x=8, y=0), index_to_tile(4), Port.LeftTop)


def test_generate_first_move_no_valid_moves() -> None:
    # No possible first moves
    third_s = ThirdS()
    bs = BoardState()

    bs = bs.with_tile(index_to_tile(0), BoardPosition(2, 0))
    bs = bs.with_tile(index_to_tile(1), BoardPosition(3, 0))
    bs = bs.with_tile(index_to_tile(2), BoardPosition(5, 0))
    bs = bs.with_tile(index_to_tile(3), BoardPosition(7, 0))
    bs = bs.with_tile(index_to_tile(4), BoardPosition(9, 0))
    bs = bs.with_tile(index_to_tile(5), BoardPosition(9, 2))
    bs = bs.with_tile(index_to_tile(6), BoardPosition(9, 4))
    bs = bs.with_tile(index_to_tile(7), BoardPosition(9, 6))
    bs = bs.with_tile(index_to_tile(8), BoardPosition(9, 8))
    bs = bs.with_tile(index_to_tile(9), BoardPosition(8, 9))
    bs = bs.with_tile(index_to_tile(10), BoardPosition(6, 9))
    bs = bs.with_tile(index_to_tile(11), BoardPosition(4, 9))
    bs = bs.with_tile(index_to_tile(12), BoardPosition(2, 9))
    bs = bs.with_tile(index_to_tile(13), BoardPosition(0, 9))
    bs = bs.with_tile(index_to_tile(14), BoardPosition(0, 7))
    bs = bs.with_tile(index_to_tile(15), BoardPosition(0, 5))
    bs = bs.with_tile(index_to_tile(16), BoardPosition(0, 3))
    bs = bs.with_tile(index_to_tile(17), BoardPosition(0, 1))

    r = third_s.generate_first_move(
        [index_to_tile(22), index_to_tile(23), index_to_tile(4)], bs
    )
    assert r.is_error()
    assert r.error() == "Failed to find a valid initial move!"


def test_generate_move_no_valid_moves() -> None:
    # No possible moves, chooses second option without rotation
    third_s = ThirdS()
    third_s.set_color(AllColors[0])
    third_s.set_rule_checker(RuleChecker())
    b = Board()
    assert b.initial_move(
        InitialMove(
            BoardPosition(1, 0), index_to_tile(34), Port.BottomRight, third_s.color
        )
    ).is_ok()

    tiles = [
        Tile(
            cast(
                List[Tuple[PortID, PortID]],
                [tuple(Port.all()[i : i + 2]) for i in range(0, len(Port.all()), 2)],
            )
        ),
        Tile(
            cast(
                List[Tuple[PortID, PortID]],
                [tuple(Port.all()[i : i + 2]) for i in range(0, len(Port.all()), 2)],
            )
        ),
    ]
    r = third_s.generate_move(tiles, b.get_board_state())
    assert id(r.assert_value()) == id(tiles[1])


def test_generate_move_needs_rotation() -> None:
    # Test that the first tile is rotated to a valid rotation when the second tile is invalid
    third_s = ThirdS()
    third_s.set_color(AllColors[0])
    third_s.set_rule_checker(RuleChecker())
    b = Board()
    b.initial_move(
        InitialMove(
            BoardPosition(9, 0), index_to_tile(34), Port.BottomRight, third_s.color
        )
    )

    tiles = [index_to_tile(11), index_to_tile(34)]
    r = third_s.generate_move(tiles, b.get_board_state())
    assert r.assert_value().edges == tiles[0].rotate().edges


def test_generate_move_takes_second_tile_no_rotation() -> None:
    # Test that the second tile is taken when valid
    third_s = ThirdS()
    third_s.set_color(AllColors[0])
    third_s.set_rule_checker(RuleChecker())
    b = Board()
    b.initial_move(
        InitialMove(
            BoardPosition(4, 0), index_to_tile(34), Port.BottomRight, third_s.color
        )
    )

    tiles = [index_to_tile(34), index_to_tile(6)]
    r = third_s.generate_move(tiles, b.get_board_state())
    assert r.assert_value().edges == tiles[1].edges
