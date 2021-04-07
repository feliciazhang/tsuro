"""
Represents the actions as defined in Assignment 4 for testing harnesses
"""
from dataclasses import dataclass

from Common.color import ColorString
from Common.tsuro_types import JSON, NetworkPortID, RotationAngle, TileIndex
from Common.validation import validate_types


@dataclass
class TilePat:
    """
    Describes a tile and the rotation of the tile via a tile index and a rotation angle
    """

    tile_index: TileIndex
    rotation_angle: RotationAngle

    @validate_types
    def to_json(self) -> JSON:
        """
        Convert this TilePat to a JSON value containing the tile index and rotation angle according to Assignment 4
        :return:    A JSON value
        """
        return [self.tile_index, self.rotation_angle]

    @staticmethod
    @validate_types
    def from_json(json_val: JSON) -> "TilePat":
        """
        Convert the given JSON value to a TilePat according to the JSON value spec defined in Assignment 4
        :param json_val:    A JSON value
        :return:            A TilePat
        """
        tile_index: TileIndex = json_val[0]
        rotation_angle: RotationAngle = json_val[1]
        return TilePat(tile_index, rotation_angle)


@dataclass
class InitialPlace:
    """
    Represents an 'InitialPlace' as defined in Assignment 4. This represents the final resting state of a
    player in a given board state.
    """

    tile_pat: TilePat
    player: ColorString
    port: NetworkPortID
    x_index: int
    y_index: int

    @validate_types
    def to_json(self) -> JSON:
        """
        Convert this InitialPlace to a JSON value containing the tile pat, player, port, and coordinates according
        to Assignment 4
        :return:    A JSON value
        """
        return [
            self.tile_pat.to_json(),
            self.player,
            self.port,
            self.x_index,
            self.y_index,
        ]

    @staticmethod
    @validate_types
    def from_json(json_val: JSON) -> "InitialPlace":
        """
        Convert the given JSON value to a InitialPlace according to the JSON value spec defined in Assignment 4
        :param json_val:    A JSON value
        :return:            A InitialPlace
        """
        tile_pat: TilePat = TilePat.from_json(json_val[0])
        player: ColorString = json_val[1]
        port: NetworkPortID = json_val[2]
        x_index: int = json_val[3]
        y_index: int = json_val[4]
        return InitialPlace(tile_pat, player, port, x_index, y_index)


@dataclass
class IntermediatePlace:
    """
    Represents an 'IntermediatePlace' as defined in Assignment 4. This represents a tile that is placed on the board
    that does not have a player placed on it in the final resting state of the board.
    """

    tile_pat: TilePat
    x_index: int
    y_index: int

    @validate_types
    def to_json(self) -> JSON:
        """
        Convert this IntermediatePlace to a JSON value containing the tile pat and coordinates according to
        Assignment 4
        :return:    A JSON value
        """
        return [self.tile_pat.to_json(), self.x_index, self.y_index]

    @staticmethod
    @validate_types
    def from_json(json_val: JSON) -> "IntermediatePlace":
        """
        Convert the given JSON value to a IntermediatePlace according to the JSON value spec defined in Assignment 4
        :param json_val:    A JSON value
        :return:            A IntermediatePlace
        """
        tile_pat: TilePat = TilePat.from_json(json_val[0])
        x_index: int = json_val[1]
        y_index: int = json_val[2]
        return IntermediatePlace(tile_pat, x_index, y_index)


@dataclass
class ActionPat:
    """
    Represents an 'ActionPat' as defined in Assignment 4. This represents a tile that is being placed by a player on
    an existing board.
    """

    player: ColorString
    tile_pat: TilePat

    @validate_types
    def to_json(self) -> JSON:
        """
        Convert this ActionPat to a JSON value containing the tile pat and player according to Assignment 4
        :return:    A JSON value
        """
        return [self.player, self.tile_pat.to_json()]

    @staticmethod
    @validate_types
    def from_json(json_val: JSON) -> "ActionPat":
        """
        Convert the given JSON value to a ActionPat according to the JSON value spec defined in Assignment 4
        :param json_val:    A JSON value
        :return:            A ActionPat
        """
        player: ColorString = json_val[0]
        tile_pat: TilePat = TilePat.from_json(json_val[1])
        return ActionPat(player, tile_pat)
