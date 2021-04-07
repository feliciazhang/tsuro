"""
A module to represent a Tsuro tile. A Tsuro tile is a square with 8 ports along the edges of the square, two
one each side. The ports are assigned PortIDs that are numbered like so:

|-----0------1------|
|                   |
7                   2
|                   |
|                   |
6                   3
|                   |
|                   |
------5------4-------

A Tile is described by a list of edges going from a numbered port to a different numbered port. Eg for the
tile where every port is connected to the port on the same side:

```
Tile([(0,1), (2,3), (4,5), (6,7)])
```

Note that equality for Tiles is defined such that if you rotate a Tile by 90, 180, or 270 degrees it is
considered to be an equal Tile.
"""

import json
import os
from functools import lru_cache
from typing import Any, Iterator, List, Mapping, NewType, Optional, Tuple, cast

from Common.color import ColorString
from Common.tsuro_types import NetworkPortID, RotationAngle, TileIndex
from Common.util import flatten, get_tsuro_root_path
from Common.validation import validate_types

# The size of rendered tiles in pixels
RENDERED_TILE_SIZE = 100

# Represents a unique ID for each port on a tile
PortID = NewType("PortID", int)


class Port:
    """
    Represents an enumeration of the possible PortIDs
    """

    TopLeft = PortID(0)
    TopRight = PortID(1)
    RightTop = PortID(2)
    RightBottom = PortID(3)
    BottomRight = PortID(4)
    BottomLeft = PortID(5)
    LeftBottom = PortID(6)
    LeftTop = PortID(7)

    @staticmethod
    @validate_types
    def all() -> List[PortID]:
        """
        Get all of the defined port IDs in clockwise order starting at the top left
        :return:    A list of port IDs
        """
        return [
            Port.TopLeft,
            Port.TopRight,
            Port.RightTop,
            Port.RightBottom,
            Port.BottomRight,
            Port.BottomLeft,
            Port.LeftBottom,
            Port.LeftTop,
        ]

    @staticmethod
    @validate_types
    def get_adjoining_port(port: PortID) -> PortID:
        """
        Get the port that the given port faces if two tiles were to be placed next to each other. For
        example, the top left port faces the bottom left port.

        :param port:    The ID of the port you want to check
        :return:        The port ID
        """
        if port == Port.TopLeft:
            return Port.BottomLeft
        if port == Port.TopRight:
            return Port.BottomRight
        if port == Port.RightTop:
            return Port.LeftTop
        if port == Port.RightBottom:
            return Port.LeftBottom
        if port == Port.LeftBottom:
            return Port.RightBottom
        if port == Port.LeftTop:
            return Port.RightTop
        if port == Port.BottomLeft:
            return Port.TopLeft
        if port == Port.BottomRight:
            return Port.TopRight
        raise ValueError(f"Given PortID {port} is not a valid port.")


class Tile:
    """
    Represents a Tsuro tile as described above.
    """

    def __init__(self, edges: List[Tuple[PortID, PortID]]):
        """
        Create a new Tsuro tile from the given list of edges.
        :param edges:   The list of edges on this Tsuro tile
        :raises         AssertionError if the given list of edges is invalid
        """
        assert len(edges) == 4
        assert sorted(flatten(edges)) == list(range(8))
        # For normalization purposes, store each edge as (smallerPortId, largerPortId)
        self.edges: List[Tuple[PortID, PortID]] = list(
            sorted([(min(x), max(x)) for x in edges])
        )

    @validate_types
    def rotate(self) -> "Tile":
        """
        Create a new tile that is equivalent to this one but rotated by 90 degrees clockwise.
        :return:    A copy of this tile that has been rotated 90 degrees clockwise
        """
        # Rotate a tile by adding two to each PortID and then modding by 8 to handle wrapping
        return Tile(
            [
                (PortID((port1 + 2) % 8), PortID((port2 + 2) % 8))
                for port1, port2 in self.edges
            ]
        )

    @validate_types
    def all_rotations(self) -> "List[Tile]":
        """
        Get all of the possible rotations of this tile. Returns the rotations in the order
        0 degrees clockwise, 90 degrees clockwise, 180 degrees clockwise, and 270 degrees clockwise
        from the current tile.

        :return:    A list of tiles where all tiles are equal since they are rotated versions of the
                    tile that this method was called on.
        """
        ret = []
        til = self
        for _ in range(4):
            ret.append(til)
            til = til.rotate()
        return ret

    @validate_types
    def get_port_connected_to(self, port: PortID) -> PortID:
        """
        Get the ID of the port that is connected to the given port
        :param port:    The ID of the port you are querying about
        :return:        The ID of the port it is connected to
        """
        for port1, port2 in self.edges:
            if port1 == port:
                return port2
            if port2 == port:
                return port1
        raise ValueError("A port is always connected to another port")

    @validate_types
    def to_svg(
        self, players: Optional[Mapping[PortID, List[ColorString]]] = None
    ) -> str:
        """
        Render this tile to an SVG image of this tile.

        :param players:     An optional mapping of the port ID to a color string that is meant to
                            represent which players sit on which ports. The ports will be colored
                            according to the color string.
        :return:            A string that is an SVG image of this tile
        """
        if players is None:
            players = {}

        port_to_coord = {
            Port.TopLeft: (RENDERED_TILE_SIZE / 3, 0),
            Port.TopRight: (2 * RENDERED_TILE_SIZE / 3, 0),
            Port.RightTop: (RENDERED_TILE_SIZE, RENDERED_TILE_SIZE / 3),
            Port.RightBottom: (RENDERED_TILE_SIZE, 2 * RENDERED_TILE_SIZE / 3),
            Port.BottomRight: (2 * RENDERED_TILE_SIZE / 3, RENDERED_TILE_SIZE),
            Port.BottomLeft: (RENDERED_TILE_SIZE / 3, RENDERED_TILE_SIZE),
            Port.LeftBottom: (0, 2 * RENDERED_TILE_SIZE / 3),
            Port.LeftTop: (0, RENDERED_TILE_SIZE / 3),
        }
        lines = []

        for (port1, port2) in self.edges:
            lines.append(
                '<polyline points="%s %s" stroke="#144e73" stroke-width="5" style="stroke:%s"/>'
                % (
                    str(port_to_coord[port1]).strip("()"),
                    str(port_to_coord[port2]).strip("()"),
                    "#dff2f5",
                )
            )
        for port, (x, y) in port_to_coord.items():
            animate_values = "#144e73"
            if players.get(port):
                animate_values = ";".join(players[port])
            lines.append(
                f'<circle stroke-width={3} stroke="#5cc4bf" cx="{x}" cy="{y}" r="10"> <animate '
                f'attributeName="fill" dur="{0.5 * len(players.get(port, []))}s" repeatCount="indefinite" '
                f'calcMode="discrete" '
                f'values="{animate_values}"> </circle>'
            )
        return """
        <svg width="%s" height="%s">
            <rect width="%s" height="%s" rx="15" fill="#144e73"/>
            %s
        </svg>
        """ % (
            RENDERED_TILE_SIZE,
            RENDERED_TILE_SIZE,
            RENDERED_TILE_SIZE,
            RENDERED_TILE_SIZE,
            "\n".join(lines),
        )

    @validate_types
    def _to_key(self) -> str:
        """
        Convert this tile into a string that uniquely represents this tile and all of the equivalent tiles.
        An equivalent tile is a tile that can be obtained by rotating this tile 90 degrees clockwise an
        unlimited number of times.

        Stated formally, this method has the property that:

        t1._to_key() == t2._to_key() <--> t1 == t2

        :return:    A string that uniquely represents this tile.
        """
        rotations = [self.edges]
        tmp = self
        for _ in range(3):
            tmp = tmp.rotate()
            rotations.append(tmp.edges)
        return str(list(sorted(rotations)))

    def __str__(self) -> str:
        return f"Tile(idx={tile_to_index(self)}, edges={self.edges})"

    def __repr__(self) -> str:
        return str(self)

    def __hash__(self) -> int:
        return hash(self._to_key())

    def __eq__(self, other: Any) -> bool:
        if isinstance(other, Tile):
            return self._to_key() == other._to_key()  # pylint: disable=protected-access
        return False


@validate_types
def _generate_tsuro_edges(
    remaining_ports: List[PortID]
) -> Iterator[List[Tuple[PortID, PortID]]]:
    """
    Divide the given list of ports into an iterator of a list of paired integers where the order of
    paired integers does not matter. Example:

    _generate_tsuro_edges([0, 1, 2, 3]) ==> [
        [(0, 1), (2, 3)],
        [(0, 2), (1, 3)],
        [(0, 3), (1, 2)],
    ]

    This function is meant to be used to generate a list of edges for Tsuro tiles. Note that by
    the Tsuro definition of tile equality, this will return duplicate Tsuro tiles.

    :param remaining_ports:     The list of ports. Must be of an even length.
    :return:                    An iterator of Tsuro tile edges
    """
    if remaining_ports == []:
        yield []
    else:
        starting_port = remaining_ports[0]
        rest = remaining_ports[1:]
        for ending_port_idx, ending_port in enumerate(rest):
            for rest_paired in _generate_tsuro_edges(
                rest[:ending_port_idx] + rest[ending_port_idx + 1 :]
            ):
                yield [(starting_port, ending_port)] + rest_paired


@lru_cache()
@validate_types
def make_tiles() -> List[Tile]:
    """
    Generate a list of the 35 valid Tsuro tiles with no duplicates

    :return:  A list of valid Tsuro tiles
    """
    return list(set(Tile(x) for x in _generate_tsuro_edges(Port.all())))


"""
Network port IDs are laid out like so around a tile:

 |-----"A"------"B"------|
 |                       |
"H"                      "C"
 |                       |
 |                       |
"G"                      "D"
 |                       |
 |                       |
 ------"F"------"E"-------
"""


PORT_MAPPINGS: List[Tuple[NetworkPortID, PortID]] = [
    ("A", Port.TopLeft),
    ("B", Port.TopRight),
    ("C", Port.RightTop),
    ("D", Port.RightBottom),
    ("E", Port.BottomRight),
    ("F", Port.BottomLeft),
    ("G", Port.LeftBottom),
    ("H", Port.LeftTop),
]


@validate_types
def network_port_id_to_port_id(port: NetworkPortID) -> PortID:
    """
    Convert the given "network port" ID to a native Port ID. See the above comment for a description
    of the layout of network ports around a tile.

    :param port:    The network port ID
    :return:        A native port ID
    """
    for network_port, port_id in PORT_MAPPINGS:
        if network_port == port:
            return port_id
    raise ValueError(f"port {port} is not a valid port")


@validate_types
def port_id_to_network_port_id(port: PortID) -> NetworkPortID:
    """
    Convert the given native port ID to a network port ID
    :param port:    The native port ID
    :return:        The network port
    """
    for network_port, port_id in PORT_MAPPINGS:
        if port_id == port:
            return network_port
    raise ValueError(f"PortID {port} is not a valid PortID")


@validate_types
def tile_pattern_to_tile(tile_index: TileIndex, degrees: RotationAngle) -> Tile:
    """
    Converts the given tile pattern components (a tile index and a rotation angle) into a Tile.

    :param tile_index:  The tile index that identifies the tile
    :param degrees:     The angle that the tile at the specified index should be rotated by
    :return:            A tile that corresponds to the arguments
    """
    til = index_to_tile(tile_index)
    remaining_degrees: int = degrees
    while remaining_degrees > 0:
        til = til.rotate()
        remaining_degrees -= 90
    return til


@validate_types
def _json_tile_to_tile(json_tile: Mapping[Any, Any]) -> Tile:
    """
    Convert the given JSON tile data to a native tile. See `Tsuro/Static/tsuro-tiles-index.json` for
    examples of JSON tiles.

    :param json_tile:   A JSON tile
    :return:            A native tile
    """
    return Tile(
        [
            (network_port_id_to_port_id(start), network_port_id_to_port_id(end))
            for start, end in json_tile["edges"]
        ]
    )


@lru_cache()
@validate_types
def load_tiles_from_json() -> List[Tuple[TileIndex, Tile]]:
    """
    Load the defined list of 35 tiles from the predefined list of tiles stored in Static/

    :return:    A list of (tile_index, tile)
    """
    ret = []

    with open(
        os.path.join(get_tsuro_root_path(), "Static/tsuro-tiles-index.json")
    ) as file:
        for idx, line in enumerate(file.readlines()):
            ret.append((cast(TileIndex, idx), _json_tile_to_tile(json.loads(line))))

    return ret


@validate_types
def tile_to_index(tile: Tile) -> TileIndex:
    """
    Convert a tile to a tile_index. A tile index is an int between 0 and 34 inclusive that uniquely
    identifies a tile based off of the static tiles in Static/

    :param tile:    The tile to convert
    :return:        The tile index
    """
    for idx, til in load_tiles_from_json():
        if til == tile:
            return idx
    raise ValueError("Failed to convert tile %s to an index!" % tile)


@validate_types
def index_to_tile(idx: TileIndex) -> Tile:
    """
    Convert a tile index to a tile. A tile index is an int between 0 and 34 inclusive that uniquely
    identifies a tile based off of the static tiles in Static/

    :param tile:    The tile to convert
    :return:        The tile index
    """
    for index, tile in load_tiles_from_json():
        if index == idx:
            return tile
    raise ValueError("Failed to convert index %s to a tile!" % idx)


@validate_types
def tile_to_rotation_angle(tile: Tile) -> RotationAngle:
    """
    Get the rotation angle of the given tile relative to the matching tile defined by a tile index.

    :param tile:    The tile to measure the rotation angle of
    :return:        The rotation angle relative to the master copy of the tile as defined in
                    `Static/tsuro-tiles-index.json`
    """
    base = index_to_tile(tile_to_index(tile))
    for angle, rot in zip([0, 90, 180, 270], base.all_rotations()):
        if rot.edges == tile.edges:
            return cast(RotationAngle, angle)
    raise ValueError(f"Failed to calculate the rotation angle for the tile {tile}")

@validate_types
def tile_to_tile_pattern(tile: Tile) -> [TileIndex, RotationAngle]:
    """
    Get the tile-pat for the given tile

    :param tile:    The tile to get the tile-pat for
    """
    return [tile_to_index(tile), tile_to_rotation_angle(tile)]
