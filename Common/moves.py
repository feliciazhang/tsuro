"""
Holds the data definitions for initial and intermediate Tsuro moves as done by players
"""
from dataclasses import dataclass

from Common.board_position import BoardPosition
from Common.color import AllColors, ColorString
from Common.tiles import Port, PortID, Tile


@dataclass(frozen=True)
class InitialMove:
    """
    Represents an initial Tsuro move of placing the given tile at the given position and port by the
    specified player
    """

    pos: BoardPosition
    tile: Tile
    port: PortID
    player: ColorString

    def __post_init__(self) -> None:
        if not isinstance(self.tile, Tile):
            raise ValueError("Created an InitialMove with an invalid tile!")
        if self.player not in AllColors:
            raise ValueError("Created an InitialMove with an invalid player!")
        if not isinstance(self.pos, BoardPosition):
            raise ValueError("Created an InitialMove with an invalid board position!")
        if self.port not in Port.all():
            raise ValueError("Created an InitialMove with an invalid port!")


@dataclass(frozen=True)
class IntermediateMove:
    """
    Represents an intermediate Tsuro move of placing the given tile by the given player
    """

    tile: Tile
    player: ColorString

    def __post_init__(self) -> None:
        if self.tile is None:
            raise ValueError("Created an IntermediateMove with no tile!")
        if not isinstance(self.tile, Tile):
            raise ValueError("Created an IntermediateMove with an invalid tile!")
        if self.player not in AllColors:
            raise ValueError("Created an IntermediateMove with an invalid player!")
