# pylint: skip-file
from Common.board_position import BoardPosition
from Common.board_state import BoardState
from Common.tiles import Port, index_to_tile
from Player.first_s import FirstS


def test_generate_first_move_1_0() -> None:
    # The first move is just placing a tile at 0,1
    first_s = FirstS()
    bs = BoardState()

    r = first_s.generate_first_move(
        [index_to_tile(22), index_to_tile(23), index_to_tile(24)], bs
    )
    assert r.assert_value() == (
        BoardPosition(x=1, y=0),
        index_to_tile(24),
        Port.RightTop,
    )


def test_generate_first_move_5_0() -> None:
    # The first move is placing a tile at 5,0 since there are tiles blocking the other positions
    first_s = FirstS()
    bs = BoardState()

    bs = bs.with_tile(index_to_tile(0), BoardPosition(1, 0))
    bs = bs.with_tile(index_to_tile(0), BoardPosition(1, 0))
    bs = bs.with_tile(index_to_tile(1), BoardPosition(3, 0))

    r = first_s.generate_first_move(
        [index_to_tile(22), index_to_tile(23), index_to_tile(3)], bs
    )
    assert r.assert_value() == (
        BoardPosition(x=5, y=0),
        index_to_tile(3),
        Port.RightTop,
    )


def test_generate_first_move_9_0() -> None:
    # The first move is placing a tile at 9,0 since there are tiles blocking the other positions
    first_s = FirstS()
    bs = BoardState()

    bs = bs.with_tile(index_to_tile(0), BoardPosition(1, 0))
    bs = bs.with_tile(index_to_tile(1), BoardPosition(3, 0))
    bs = bs.with_tile(index_to_tile(2), BoardPosition(5, 0))
    bs = bs.with_tile(index_to_tile(3), BoardPosition(7, 0))

    r = first_s.generate_first_move(
        [index_to_tile(22), index_to_tile(23), index_to_tile(4)], bs
    )
    assert r.assert_value() == (
        BoardPosition(x=9, y=0),
        index_to_tile(4),
        Port.BottomRight,
    )


def test_generate_first_move_9_2() -> None:
    # The first move is placing a tile at 9,2 since there are tiles blocking the other positions
    first_s = FirstS()
    bs = BoardState()

    bs = bs.with_tile(index_to_tile(0), BoardPosition(1, 0))
    bs = bs.with_tile(index_to_tile(1), BoardPosition(3, 0))
    bs = bs.with_tile(index_to_tile(2), BoardPosition(5, 0))
    bs = bs.with_tile(index_to_tile(3), BoardPosition(7, 0))
    bs = bs.with_tile(index_to_tile(4), BoardPosition(9, 0))

    r = first_s.generate_first_move(
        [index_to_tile(22), index_to_tile(23), index_to_tile(4)], bs
    )
    assert r.assert_value() == (BoardPosition(x=9, y=2), index_to_tile(4), Port.TopLeft)


def test_generate_first_move_9_8() -> None:
    # The first move is placing a tile at 9,8 since there are tiles blocking the other positions
    first_s = FirstS()
    bs = BoardState()

    bs = bs.with_tile(index_to_tile(0), BoardPosition(1, 0))
    bs = bs.with_tile(index_to_tile(1), BoardPosition(3, 0))
    bs = bs.with_tile(index_to_tile(2), BoardPosition(5, 0))
    bs = bs.with_tile(index_to_tile(3), BoardPosition(7, 0))
    bs = bs.with_tile(index_to_tile(4), BoardPosition(9, 0))
    bs = bs.with_tile(index_to_tile(5), BoardPosition(9, 2))
    bs = bs.with_tile(index_to_tile(6), BoardPosition(9, 4))
    bs = bs.with_tile(index_to_tile(7), BoardPosition(9, 6))

    r = first_s.generate_first_move(
        [index_to_tile(22), index_to_tile(23), index_to_tile(4)], bs
    )
    assert r.assert_value() == (BoardPosition(x=9, y=8), index_to_tile(4), Port.TopLeft)


def test_generate_first_move_8_9() -> None:
    # The first move is placing a tile at 8,9 since there are tiles blocking the other positions
    first_s = FirstS()
    bs = BoardState()

    bs = bs.with_tile(index_to_tile(0), BoardPosition(1, 0))
    bs = bs.with_tile(index_to_tile(1), BoardPosition(3, 0))
    bs = bs.with_tile(index_to_tile(2), BoardPosition(5, 0))
    bs = bs.with_tile(index_to_tile(3), BoardPosition(7, 0))
    bs = bs.with_tile(index_to_tile(4), BoardPosition(9, 0))
    bs = bs.with_tile(index_to_tile(5), BoardPosition(9, 2))
    bs = bs.with_tile(index_to_tile(6), BoardPosition(9, 4))
    bs = bs.with_tile(index_to_tile(7), BoardPosition(9, 6))
    bs = bs.with_tile(index_to_tile(8), BoardPosition(9, 8))

    r = first_s.generate_first_move(
        [index_to_tile(22), index_to_tile(23), index_to_tile(4)], bs
    )
    assert r.assert_value() == (BoardPosition(x=8, y=9), index_to_tile(4), Port.TopLeft)


def test_generate_first_move_4_9() -> None:
    # The first move is placing a tile at 4,9 since there are tiles blocking the other positions
    first_s = FirstS()
    bs = BoardState()

    bs = bs.with_tile(index_to_tile(0), BoardPosition(1, 0))
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

    r = first_s.generate_first_move(
        [index_to_tile(22), index_to_tile(23), index_to_tile(4)], bs
    )
    assert r.assert_value() == (BoardPosition(x=4, y=9), index_to_tile(4), Port.TopLeft)


def test_generate_first_move_0_9() -> None:
    # The first move is placing a tile at 0,9 since there are tiles blocking the other positions
    first_s = FirstS()
    bs = BoardState()

    bs = bs.with_tile(index_to_tile(0), BoardPosition(1, 0))
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

    r = first_s.generate_first_move(
        [index_to_tile(22), index_to_tile(23), index_to_tile(4)], bs
    )
    assert r.assert_value() == (BoardPosition(x=0, y=9), index_to_tile(4), Port.TopLeft)


def test_generate_first_move_0_5() -> None:
    # The first move is placing a tile at 0,5 since there are tiles blocking the other positions
    first_s = FirstS()
    bs = BoardState()

    bs = bs.with_tile(index_to_tile(0), BoardPosition(1, 0))
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

    r = first_s.generate_first_move(
        [index_to_tile(22), index_to_tile(23), index_to_tile(4)], bs
    )
    assert r.assert_value() == (BoardPosition(x=0, y=5), index_to_tile(4), Port.TopLeft)


def test_generate_first_move_0_1() -> None:
    # The first move is placing a tile at 0,1 since there are tiles blocking the other positions
    first_s = FirstS()
    bs = BoardState()

    bs = bs.with_tile(index_to_tile(0), BoardPosition(1, 0))
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

    r = first_s.generate_first_move(
        [index_to_tile(22), index_to_tile(23), index_to_tile(4)], bs
    )
    assert r.assert_value() == (BoardPosition(x=0, y=1), index_to_tile(4), Port.TopLeft)


def test_generate_first_move_0_0() -> None:
    # The first move is placing a tile at 0,0 since there are tiles blocking the other positions
    first_s = FirstS()
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
    bs = bs.with_tile(index_to_tile(17), BoardPosition(0, 2))

    r = first_s.generate_first_move(
        [index_to_tile(22), index_to_tile(23), index_to_tile(4)], bs
    )
    assert r.assert_value() == (
        BoardPosition(x=0, y=0),
        index_to_tile(4),
        Port.RightTop,
    )


def test_generate_first_move_no_valid_moves() -> None:
    # No possible first moves
    first_s = FirstS()
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

    r = first_s.generate_first_move(
        [index_to_tile(22), index_to_tile(23), index_to_tile(4)], bs
    )
    assert r.is_error()
    assert r.error() == "Failed to find a valid initial move!"


def test_generate_move() -> None:
    # Generate move just always returns the first tile
    first_s = FirstS()
    bs = BoardState()

    assert first_s.generate_move(
        [index_to_tile(1), index_to_tile(2)], bs
    ).assert_value() == index_to_tile(1)
    assert first_s.generate_move(
        [index_to_tile(3), index_to_tile(2)], bs
    ).assert_value() == index_to_tile(3)


def test_incorrect_number_tiles_given() -> None:
    first_s = FirstS()
    bs = BoardState()

    r = first_s.generate_move(
        [index_to_tile(1), index_to_tile(2), index_to_tile(3)], bs
    )
    assert r.is_error()
    assert r.error() == "Strategy.generate_move given 3 (expected 2)"

    r2 = first_s.generate_first_move([index_to_tile(1), index_to_tile(2)], bs)
    assert r2.is_error()
    assert r2.error() == "Strategy.generate_first_move given 2 (expected 3)"
