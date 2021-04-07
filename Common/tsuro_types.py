"""
Holds a variety of type definitions used in Tsuro to be used with mypy for type checking
this implementation of Tsuro
"""
from typing import Any, List, Set, Tuple

from typing_extensions import Literal

from Common.color import ColorString

# A type meant to represent JSON
JSON = Any

# A type meant to represent port IDs on tiles as defined by Matthias (aka the network protocol)
NetworkPortID = Literal["A", "B", "C", "D", "E", "F", "G", "H"]

# A type meant to represent the possible tile indices as defined by Matthias and
# in `Static/tsuro-tiles-index.json`
TileIndex = Literal[
    0,
    1,
    2,
    3,
    4,
    5,
    6,
    7,
    8,
    9,
    10,
    11,
    12,
    13,
    14,
    15,
    16,
    17,
    18,
    19,
    20,
    21,
    22,
    23,
    24,
    25,
    26,
    27,
    28,
    29,
    30,
    31,
    32,
    33,
    34,
]

# A type meant to represent the possible rotation angles. A rotation angle represents a clockwise
# rotation of a Tsuro tile by 0, 90, 180, or 270 degrees.
RotationAngle = Literal[0, 90, 180, 270]

# Represents the results of running a single game of Tsuro. The first element of the tuple is a list of
# sets. The first element of this list is the players who tied for first place, the second element is
# the players who tied for second place, and so on. The second element of the tuple is the set of
# players that cheated during the game. It is guaranteed that each color string that participated in
# a game occurs in the game result exactly once.
GameResult = Tuple[List[Set[ColorString]], Set[ColorString]]
