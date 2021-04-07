"""
A module that holds the data structure that represents a board position
"""
from typing import Any

from Common.validation import validate_types

MIN_BOARD_COORDINATE = 0
MAX_BOARD_COORDINATE = 9


class BoardPosition:
    """
    Represents a position on the board as x and y coordinates. x and y are zero-indexed coordinates
    starting in the top left corner of the board (eg 0,0 means the top-left corner and 9,9 means the
    bottom-right corner). x and y must be in the range 0 to 9 inclusive.
    """

    x: int
    y: int

    def __init__(self, x: int, y: int) -> None:
        if not (MIN_BOARD_COORDINATE <= x <= 9 and MIN_BOARD_COORDINATE <= y <= 9):
            raise ValueError(
                "BoardPosition must be given coordinates between 0 and 9 inclusive!"
            )
        self.x = x
        self.y = y

    @validate_types
    def is_corner(self) -> bool:
        """
        Returns whether or not this BoardPosition is on the corner of a square board (with dimensions
        MIN_BOARD_COORDINATE and MAX_BOARD_COORDINATE)

        :return:    Whether it is on a corner
        """
        return (
            self.x == MIN_BOARD_COORDINATE
            and (self.y == MIN_BOARD_COORDINATE or self.y == MAX_BOARD_COORDINATE)
        ) or (
            self.x == MAX_BOARD_COORDINATE
            and (self.y == MIN_BOARD_COORDINATE or self.y == MAX_BOARD_COORDINATE)
        )

    @validate_types
    def is_edge(self) -> bool:
        """
        Returns whether or not this BoardPosition is on the edge of a square board (with dimensions
        MIN_BOARD_COORDINATE and MAX_BOARD_COORDINATE)

        :return:    Whether it is on an edge
        """
        return self.x in [MIN_BOARD_COORDINATE, MAX_BOARD_COORDINATE] or self.y in [
            MIN_BOARD_COORDINATE,
            MAX_BOARD_COORDINATE,
        ]

    def __str__(self) -> str:
        return "BoardPosition(x=%s, y=%s)" % (self.x, self.y)

    def __repr__(self) -> str:
        return str(self)

    def __eq__(self, other: Any) -> bool:
        if isinstance(other, BoardPosition):
            return self.x == other.x and self.y == other.y
        return False

    def __hash__(self) -> int:
        return hash((self.x, self.y))

    def __deepcopy__(self, memo: Any) -> "BoardPosition":
        return BoardPosition(self.x, self.y)
