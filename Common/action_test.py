# pylint: skip-file
from Common.action import ActionPat, InitialPlace, IntermediatePlace, TilePat


def test_tile_pat() -> None:
    t = TilePat.from_json([22, 90])
    assert t.tile_index == 22
    assert t.rotation_angle == 90
    assert t.to_json() == [22, 90]


def test_initial_place() -> None:
    json_rep = [[22, 90], "red", "B", 5, 6]
    ip = InitialPlace.from_json(json_rep)

    assert ip.tile_pat == TilePat(22, 90)
    assert ip.player == "red"
    assert ip.port == "B"
    assert ip.x_index == 5
    assert ip.y_index == 6
    assert ip.to_json() == json_rep


def test_intermediate_place() -> None:
    json_rep = [[15, 180], 8, 2]
    ip = IntermediatePlace.from_json(json_rep)

    assert ip.tile_pat == TilePat(15, 180)
    assert ip.x_index == 8
    assert ip.y_index == 2
    assert ip.to_json() == json_rep


def test_action_pat() -> None:
    json_rep = ["red", [7, 270]]
    ap = ActionPat.from_json(json_rep)

    assert ap.tile_pat == TilePat(7, 270)
    assert ap.player == "red"
    assert ap.to_json() == json_rep
