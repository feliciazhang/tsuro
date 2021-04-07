# pylint: skip-file
import pytest

from Common.board_position import BoardPosition


def test_board_position() -> None:
    with pytest.raises(ValueError):
        BoardPosition(-1, 0)
    with pytest.raises(ValueError):
        BoardPosition(0, 100)

    assert BoardPosition(5, 3) == BoardPosition(5, 3)
    assert hash(BoardPosition(5, 3)) == hash(BoardPosition(5, 3))
    assert BoardPosition(5, 3) != BoardPosition(5, 4)
    assert hash(BoardPosition(5, 3)) != hash(BoardPosition(5, 4))
    assert BoardPosition(5, 3) != {}

    b = BoardPosition(2, 8)
    assert str(b) == repr(b) == "BoardPosition(x=2, y=8)"


def test_is_corner_is_edge() -> None:
    assert BoardPosition(0, 0).is_corner()
    assert BoardPosition(9, 0).is_corner()
    assert BoardPosition(0, 9).is_corner()
    assert BoardPosition(9, 9).is_corner()

    assert BoardPosition(0, 0).is_edge()
    assert BoardPosition(9, 0).is_edge()
    assert BoardPosition(0, 9).is_edge()
    assert BoardPosition(9, 9).is_edge()

    assert BoardPosition(0, 5).is_edge()
    assert BoardPosition(9, 3).is_edge()
    assert BoardPosition(7, 9).is_edge()
    assert BoardPosition(9, 2).is_edge()
