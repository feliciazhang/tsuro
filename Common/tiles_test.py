# pylint: skip-file

from typing import cast

import pytest

from Common import tiles
from Common.tiles import Port
from Common.tsuro_types import TileIndex
from Common.validation import disable_validation

EXPECTED_NUMBER_TILES = 35


def test_make_tiles() -> None:
    assert len(tiles.make_tiles()) == EXPECTED_NUMBER_TILES
    assert len(set(tiles.make_tiles())) == EXPECTED_NUMBER_TILES
    for t in tiles.make_tiles():
        assert t == t.rotate()
        assert t == t.rotate().rotate()
        assert t == t.rotate().rotate().rotate()


def test_rotate_simple() -> None:
    t1 = tiles.Tile([(0, 1), (2, 3), (4, 5), (6, 7)])  # type: ignore
    t2 = t1.rotate()
    t3 = t2.rotate()
    t4 = t3.rotate()
    t5 = t4.rotate()
    assert t1 == t2 == t3 == t4 == t5
    assert t1.edges == t2.edges == t3.edges == t4.edges == t5.edges


def test_rotate_complex() -> None:
    t1 = tiles.Tile([(0, 2), (1, 6), (3, 5), (4, 7)])  # type: ignore
    t2 = t1.rotate()
    t3 = t2.rotate()
    t4 = t3.rotate()
    t5 = t4.rotate()
    assert t1 == t2 == t3 == t4 == t5
    assert t1.edges == t5.edges == [(0, 2), (1, 6), (3, 5), (4, 7)]
    assert t2.edges == [(0, 3), (1, 6), (2, 4), (5, 7)]
    assert t3.edges == [(0, 3), (1, 7), (2, 5), (4, 6)]
    assert t4.edges == [(0, 6), (1, 3), (2, 5), (4, 7)]


def test_all_rotations() -> None:
    t1 = tiles.Tile([(0, 2), (1, 6), (3, 5), (4, 7)])  # type: ignore
    assert len(t1.all_rotations()) == 4
    assert len(set(t1.all_rotations())) == 1
    assert len(set([tuple(x.edges) for x in t1.all_rotations()])) == 4


def test_get_port_connected_to() -> None:
    t1 = tiles.Tile(
        [
            (tiles.Port.LeftTop, tiles.Port.RightBottom),
            (tiles.Port.LeftBottom, tiles.Port.RightTop),
            (tiles.Port.TopRight, tiles.Port.TopLeft),
            (tiles.Port.BottomRight, tiles.Port.BottomLeft),
        ]
    )
    assert t1.get_port_connected_to(tiles.Port.LeftTop) == tiles.Port.RightBottom
    assert t1.get_port_connected_to(tiles.Port.RightBottom) == tiles.Port.LeftTop
    assert t1.get_port_connected_to(tiles.Port.LeftBottom) == tiles.Port.RightTop
    assert t1.get_port_connected_to(tiles.Port.RightTop) == tiles.Port.LeftBottom
    assert t1.get_port_connected_to(tiles.Port.TopRight) == tiles.Port.TopLeft
    assert t1.get_port_connected_to(tiles.Port.TopLeft) == tiles.Port.TopRight
    assert t1.get_port_connected_to(tiles.Port.BottomRight) == tiles.Port.BottomLeft
    assert t1.get_port_connected_to(tiles.Port.BottomLeft) == tiles.Port.BottomRight


def test_to_svg_simple() -> None:
    t = tiles.Tile([(0, 1), (2, 3), (4, 5), (6, 7)])  # type: ignore
    # Result checked manually via inspection. If this test fails due to a change to the to_svg()
    # function, run it and manually check the resulting svg.
    assert (
        t.to_svg().strip()
        == """<svg width="100" height="100">\n            <rect width="100" height="100" rx="15" fill="#144e73"/>\n            <polyline points="33.333333333333336, 0 66.66666666666667, 0" stroke="#144e73" stroke-width="5" style="stroke:#dff2f5"/>\n<polyline points="100, 33.333333333333336 100, 66.66666666666667" stroke="#144e73" stroke-width="5" style="stroke:#dff2f5"/>\n<polyline points="66.66666666666667, 100 33.333333333333336, 100" stroke="#144e73" stroke-width="5" style="stroke:#dff2f5"/>\n<polyline points="0, 66.66666666666667 0, 33.333333333333336" stroke="#144e73" stroke-width="5" style="stroke:#dff2f5"/>\n<circle stroke-width=3 stroke="#5cc4bf" cx="33.333333333333336" cy="0" r="10"> <animate attributeName="fill" dur="0.0s" repeatCount="indefinite" calcMode="discrete" values="#144e73"> </circle>\n<circle stroke-width=3 stroke="#5cc4bf" cx="66.66666666666667" cy="0" r="10"> <animate attributeName="fill" dur="0.0s" repeatCount="indefinite" calcMode="discrete" values="#144e73"> </circle>\n<circle stroke-width=3 stroke="#5cc4bf" cx="100" cy="33.333333333333336" r="10"> <animate attributeName="fill" dur="0.0s" repeatCount="indefinite" calcMode="discrete" values="#144e73"> </circle>\n<circle stroke-width=3 stroke="#5cc4bf" cx="100" cy="66.66666666666667" r="10"> <animate attributeName="fill" dur="0.0s" repeatCount="indefinite" calcMode="discrete" values="#144e73"> </circle>\n<circle stroke-width=3 stroke="#5cc4bf" cx="66.66666666666667" cy="100" r="10"> <animate attributeName="fill" dur="0.0s" repeatCount="indefinite" calcMode="discrete" values="#144e73"> </circle>\n<circle stroke-width=3 stroke="#5cc4bf" cx="33.333333333333336" cy="100" r="10"> <animate attributeName="fill" dur="0.0s" repeatCount="indefinite" calcMode="discrete" values="#144e73"> </circle>\n<circle stroke-width=3 stroke="#5cc4bf" cx="0" cy="66.66666666666667" r="10"> <animate attributeName="fill" dur="0.0s" repeatCount="indefinite" calcMode="discrete" values="#144e73"> </circle>\n<circle stroke-width=3 stroke="#5cc4bf" cx="0" cy="33.333333333333336" r="10"> <animate attributeName="fill" dur="0.0s" repeatCount="indefinite" calcMode="discrete" values="#144e73"> </circle>\n        </svg>"""
    )


def test_to_svg_complex() -> None:
    t = tiles.Tile([(0, 2), (1, 6), (3, 5), (4, 7)])  # type: ignore
    # Result checked manually via inspection. If this test fails due to a change to the to_svg()
    # function, run it and manually check the resulting svg.
    assert (
        t.to_svg({Port.TopRight: ["red", "green"], Port.BottomLeft: ["black"]}).strip()
        == """<svg width="100" height="100">\n            <rect width="100" height="100" rx="15" fill="#144e73"/>\n            <polyline points="33.333333333333336, 0 100, 33.333333333333336" stroke="#144e73" stroke-width="5" style="stroke:#dff2f5"/>\n<polyline points="66.66666666666667, 0 0, 66.66666666666667" stroke="#144e73" stroke-width="5" style="stroke:#dff2f5"/>\n<polyline points="100, 66.66666666666667 33.333333333333336, 100" stroke="#144e73" stroke-width="5" style="stroke:#dff2f5"/>\n<polyline points="66.66666666666667, 100 0, 33.333333333333336" stroke="#144e73" stroke-width="5" style="stroke:#dff2f5"/>\n<circle stroke-width=3 stroke="#5cc4bf" cx="33.333333333333336" cy="0" r="10"> <animate attributeName="fill" dur="0.0s" repeatCount="indefinite" calcMode="discrete" values="#144e73"> </circle>\n<circle stroke-width=3 stroke="#5cc4bf" cx="66.66666666666667" cy="0" r="10"> <animate attributeName="fill" dur="1.0s" repeatCount="indefinite" calcMode="discrete" values="red;green"> </circle>\n<circle stroke-width=3 stroke="#5cc4bf" cx="100" cy="33.333333333333336" r="10"> <animate attributeName="fill" dur="0.0s" repeatCount="indefinite" calcMode="discrete" values="#144e73"> </circle>\n<circle stroke-width=3 stroke="#5cc4bf" cx="100" cy="66.66666666666667" r="10"> <animate attributeName="fill" dur="0.0s" repeatCount="indefinite" calcMode="discrete" values="#144e73"> </circle>\n<circle stroke-width=3 stroke="#5cc4bf" cx="66.66666666666667" cy="100" r="10"> <animate attributeName="fill" dur="0.0s" repeatCount="indefinite" calcMode="discrete" values="#144e73"> </circle>\n<circle stroke-width=3 stroke="#5cc4bf" cx="33.333333333333336" cy="100" r="10"> <animate attributeName="fill" dur="0.5s" repeatCount="indefinite" calcMode="discrete" values="black"> </circle>\n<circle stroke-width=3 stroke="#5cc4bf" cx="0" cy="66.66666666666667" r="10"> <animate attributeName="fill" dur="0.0s" repeatCount="indefinite" calcMode="discrete" values="#144e73"> </circle>\n<circle stroke-width=3 stroke="#5cc4bf" cx="0" cy="33.333333333333336" r="10"> <animate attributeName="fill" dur="0.0s" repeatCount="indefinite" calcMode="discrete" values="#144e73"> </circle>\n        </svg>"""
    )


def test_str_repr() -> None:
    t = tiles.Tile([(0, 2), (1, 6), (3, 5), (4, 7)])  # type: ignore
    assert str(t) == repr(t) == "Tile(idx=14, edges=[(0, 2), (1, 6), (3, 5), (4, 7)])"
    t = tiles.Tile([(2, 0), (1, 6), (3, 5), (4, 7)])  # type: ignore
    assert str(t) == repr(t) == "Tile(idx=14, edges=[(0, 2), (1, 6), (3, 5), (4, 7)])"


def test_equals_hash() -> None:
    t1 = tiles.Tile([(0, 2), (1, 6), (3, 5), (4, 7)])  # type: ignore
    t2 = t1.rotate()
    t3 = tiles.Tile([(0, 1), (2, 3), (4, 5), (6, 7)])  # type: ignore

    assert t1 == t2
    assert t1 != t3
    assert t2 != t3
    assert hash(t1) == hash(t2)
    assert hash(t1) != hash(t3)
    assert hash(t2) != hash(t3)
    assert t1 != {}


def test_load_tiles_from_json() -> None:
    assert len(tiles.load_tiles_from_json()) == EXPECTED_NUMBER_TILES
    assert (
        len(set([i for i, t in tiles.load_tiles_from_json()])) == EXPECTED_NUMBER_TILES
    )
    assert (
        len(set([t for i, t in tiles.load_tiles_from_json()])) == EXPECTED_NUMBER_TILES
    )


def test_index_to_tile() -> None:
    seen = set()
    for i in range(0, 35):
        t = tiles.index_to_tile(cast(TileIndex, i))
        assert isinstance(t, tiles.Tile)
        seen.add(t)
    assert len(seen) == 35


def test_tile_to_index() -> None:
    seen = []
    for t in tiles.make_tiles():
        i = tiles.tile_to_index(t)
        seen.append(i)
        assert isinstance(i, int)
    assert list(sorted(seen)) == list(range(0, 35))


def test_network_port_id_to_port_id() -> None:
    assert tiles.network_port_id_to_port_id("A") == tiles.Port.TopLeft
    assert tiles.network_port_id_to_port_id("B") == tiles.Port.TopRight
    assert tiles.network_port_id_to_port_id("C") == tiles.Port.RightTop
    assert tiles.network_port_id_to_port_id("D") == tiles.Port.RightBottom
    assert tiles.network_port_id_to_port_id("E") == tiles.Port.BottomRight
    assert tiles.network_port_id_to_port_id("F") == tiles.Port.BottomLeft
    assert tiles.network_port_id_to_port_id("G") == tiles.Port.LeftBottom
    assert tiles.network_port_id_to_port_id("H") == tiles.Port.LeftTop


@disable_validation
def test_network_port_id_to_port_id_invalid() -> None:
    with pytest.raises(ValueError):
        tiles.network_port_id_to_port_id("Z")  # type: ignore


def test_port_id_to_network_port_id() -> None:
    assert tiles.port_id_to_network_port_id(tiles.Port.TopLeft) == "A"
    assert tiles.port_id_to_network_port_id(tiles.Port.TopRight) == "B"
    assert tiles.port_id_to_network_port_id(tiles.Port.RightTop) == "C"
    assert tiles.port_id_to_network_port_id(tiles.Port.RightBottom) == "D"
    assert tiles.port_id_to_network_port_id(tiles.Port.BottomRight) == "E"
    assert tiles.port_id_to_network_port_id(tiles.Port.BottomLeft) == "F"
    assert tiles.port_id_to_network_port_id(tiles.Port.LeftBottom) == "G"
    assert tiles.port_id_to_network_port_id(tiles.Port.LeftTop) == "H"
    with pytest.raises(ValueError):
        tiles.port_id_to_network_port_id(tiles.PortID(-1))


def test_tile_pattern_to_tile() -> None:
    assert tiles.tile_pattern_to_tile(22, 90) == tiles.index_to_tile(22)

    assert tiles.tile_to_rotation_angle(tiles.tile_pattern_to_tile(31, 0)) == 0
    assert tiles.tile_to_rotation_angle(tiles.tile_pattern_to_tile(31, 90)) == 90
    assert tiles.tile_to_rotation_angle(tiles.tile_pattern_to_tile(31, 180)) == 180
    assert tiles.tile_to_rotation_angle(tiles.tile_pattern_to_tile(31, 270)) == 270


def test_tile_to_rotation_angle() -> None:
    assert tiles.tile_to_rotation_angle(tiles.index_to_tile(13)) == 0
    assert tiles.tile_to_rotation_angle(tiles.index_to_tile(13).rotate()) == 90
    assert (
        tiles.tile_to_rotation_angle(tiles.index_to_tile(13).rotate().rotate()) == 180
    )
    assert (
        tiles.tile_to_rotation_angle(tiles.index_to_tile(13).rotate().rotate().rotate())
        == 270
    )
    assert tiles.tile_to_rotation_angle(tiles.index_to_tile(2)) == 0
    assert tiles.tile_to_rotation_angle(tiles.index_to_tile(2).rotate()) == 0
    assert tiles.tile_to_rotation_angle(tiles.index_to_tile(2).rotate().rotate()) == 0
    assert (
        tiles.tile_to_rotation_angle(tiles.index_to_tile(2).rotate().rotate().rotate())
        == 0
    )


def test_port_all_order() -> None:
    assert Port.all() == [
        Port.TopLeft,
        Port.TopRight,
        Port.RightTop,
        Port.RightBottom,
        Port.BottomRight,
        Port.BottomLeft,
        Port.LeftBottom,
        Port.LeftTop,
    ]

    assert Port.all() == list(sorted(Port.all()))
