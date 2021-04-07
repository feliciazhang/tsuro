# pylint: skip-file
from typing import List, Tuple

import pytest
from hypothesis import HealthCheck, given, settings  # type: ignore
from hypothesis.strategies import builds, integers, lists  # type: ignore

from Admin.referee import Referee, deterministic_tile_iterator
from Common.board_position import BoardPosition
from Common.board_state import BoardState
from Common.color import ColorString
from Common.player_interface import PlayerInterface
from Common.result import Result, error, ok
from Common.rules import RuleChecker
from Common.tiles import PortID, Tile, index_to_tile, tile_to_index
from Player.first_s import FirstS
from Player.player import Player


def make_ref() -> Referee:
    ref = Referee()
    ref.set_rule_checker(RuleChecker())
    return ref


def make_players(num_players: int) -> List[PlayerInterface]:
    return [Player(FirstS()) for _ in range(num_players)]


def test_referee_three_deterministic_players() -> None:
    ref = make_ref()
    assert ref.set_players(make_players(3)).assert_value() == ["white", "black", "red"]
    ref.set_tile_iterator(deterministic_tile_iterator())

    r = ref.run_game()

    assert r.is_ok()
    assert r.value() == ([{"white"}], {"black", "red"})


def test_referee_four_deterministic_players() -> None:
    ref = make_ref()
    assert ref.set_players(make_players(4)).assert_value() == [
        "white",
        "black",
        "red",
        "green",
    ]
    ref.set_tile_iterator(deterministic_tile_iterator())

    r = ref.run_game()

    assert r.is_ok()
    assert r.value() == ([{"black"}], {"white", "red", "green"})


def test_get_tiles() -> None:
    ref = Referee()
    ref.set_tile_iterator(deterministic_tile_iterator())

    assert ref._get_tiles(3) == [index_to_tile(0), index_to_tile(1), index_to_tile(2)]

    assert [tile_to_index(t) for t in ref._get_tiles(35)] == list(range(3, 35)) + [
        0,
        1,
        2,
    ]
    assert len(ref._get_tiles(123)) == 123


# @settings(  # type: ignore
#     suppress_health_check=[HealthCheck.large_base_example],
#     deadline=None,
#     max_examples=5,  # Can tweak this to increase coverage
# )
# @given(  # type: ignore
#     lists(builds(index_to_tile, integers(0, 34)), min_size=100), integers(3, 5)
# )
# def test_game_result_no_dupes(random_tiles: List[Tile], num_players: int) -> None:
#     ref = make_ref()
#     ref.set_tile_iterator(iter(random_tiles))
#     assert ref.set_players(make_players(num_players)).is_ok()
#     r = ref.run_game()
#     assert r.is_ok()
#     leaderboard, cheaters = r.value()
#     all_items: List[ColorString] = []
#     for colors in leaderboard:
#         all_items.extend(colors)
#     all_items.extend(cheaters)
#     assert len(all_items) == num_players
#     assert list(sorted(all_items)) == list(sorted(list(set(all_items))))


class CrashingPlayer(PlayerInterface):
    def __init__(self, crash: bool, first: bool) -> None:
        self.crash = crash
        self.first = first

    def generate_first_move(
        self, tiles: List[Tile], board_state: BoardState
    ) -> Result[Tuple[BoardPosition, Tile, PortID]]:
        if self.first:
            if self.crash:
                raise Exception("Crash!")
            else:
                return error("Error!")
        return FirstS().generate_first_move(tiles, board_state)

    def generate_move(self, tiles: List[Tile], board_state: BoardState) -> Result[Tile]:
        if self.crash:
            raise Exception("Crash!")
        else:
            return error("Error!")

    def notify_won_tournament(self) -> None:
        if self.crash:
            raise Exception("Crash!")


def test_referee_crashing_player() -> None:
    cp_exception_init = CrashingPlayer(True, True)
    cp_error_init = CrashingPlayer(False, True)
    cp_exception_inter = CrashingPlayer(True, False)
    cp_error_inter = CrashingPlayer(False, False)
    p = Player(FirstS())

    ref = make_ref()
    assert ref.set_players(
        [cp_error_init, cp_exception_init, cp_error_inter, cp_exception_inter, p]
    ).assert_value() == ["white", "black", "red", "green", "blue"]
    ref.set_tile_iterator(deterministic_tile_iterator())

    r = ref.run_game()
    assert r.is_ok()
    assert r.value() == ([{"blue"}], {"green", "red", "black", "white"})


def test_referee_allow_loop() -> None:
    tiles = [
        index_to_tile(23),
        index_to_tile(23),
        index_to_tile(23),
        index_to_tile(4),
        index_to_tile(4),
        index_to_tile(4),
        index_to_tile(4),
        index_to_tile(4),
        index_to_tile(4),
        index_to_tile(5),
        index_to_tile(5),
        index_to_tile(5),
        index_to_tile(5),
        index_to_tile(5),
        index_to_tile(5),
        index_to_tile(4),
        index_to_tile(4),
        index_to_tile(4),
        index_to_tile(2),
        index_to_tile(2),
        index_to_tile(2),
        index_to_tile(2),
        index_to_tile(2),
        index_to_tile(2),
        index_to_tile(2),
        index_to_tile(2),
        index_to_tile(2),
        index_to_tile(2),
        index_to_tile(2),
        index_to_tile(2),
        index_to_tile(11),
        index_to_tile(11),
        index_to_tile(11),
        index_to_tile(11),
        index_to_tile(11),
        index_to_tile(11),
        index_to_tile(16),
        index_to_tile(16),
        index_to_tile(16),
        index_to_tile(16).rotate(),
        index_to_tile(16).rotate(),
        index_to_tile(16).rotate(),
        index_to_tile(16).rotate(),
        index_to_tile(16).rotate(),
        index_to_tile(16).rotate(),
    ] + [index_to_tile(2)] * 1000
    players = make_players(3)
    ref = make_ref()
    ref.set_tile_iterator(iter(tiles))
    assert ref.set_players(players).is_ok()

    r = ref.run_game()
    assert r.is_ok()
    assert r.value() == ([{"black"}], {"white", "red"})


def test_referee_allow_suicide() -> None:
    tiles = [
        index_to_tile(23),
        index_to_tile(23),
        index_to_tile(23),
        index_to_tile(23),
        index_to_tile(23),
        index_to_tile(23),
        index_to_tile(23),
        index_to_tile(23),
        index_to_tile(23),
        index_to_tile(4),
        index_to_tile(4),
        index_to_tile(4),
        index_to_tile(4),
        index_to_tile(4),
        index_to_tile(4),
        index_to_tile(4),
        index_to_tile(4),
        index_to_tile(4),
        index_to_tile(4),
        index_to_tile(4),
        index_to_tile(4),
        index_to_tile(4),
        index_to_tile(4),
        index_to_tile(4),
    ]
    players = make_players(3)
    ref = make_ref()
    ref.set_tile_iterator(iter(tiles))
    assert ref.set_players(players).is_ok()

    r = ref.run_game()
    assert r.is_ok()
    assert r.value() == ([{"white", "black", "red"}], set())


def test_referee_collision() -> None:
    tiles = [index_to_tile(2)] * 1000
    players = make_players(3)
    ref = make_ref()
    ref.set_tile_iterator(iter(tiles))
    assert ref.set_players(players).is_ok()

    r = ref.run_game()
    assert r.is_ok()
    assert r.value() == ([{"white", "black", "red"}], set())


def test_set_players_error() -> None:
    ref = make_ref()
    r = ref.set_players([])
    assert r.is_error()
    assert r.error() == "there must be between 3 and 5 players, not 0."
    r = ref.set_players([Player(FirstS())] * 6)
    assert r.is_error()
    assert r.error() == "there must be between 3 and 5 players, not 6."
    r = ref.set_players([Player(FirstS())] * 4)
    assert r.is_error()
    assert (
        r.error()
        == "the given set of players contains duplicates (or players that do not implement __hash__, __eq__)"
    )
    r = ref.set_players([Player(FirstS()), Player(FirstS()), Player(FirstS())])
    assert r.is_ok()
    assert r.value() == ["white", "black", "red"]
    r = ref.set_players([Player(FirstS()), Player(FirstS()), Player(FirstS())])
    assert r.is_error()
    assert r.error() == "players have already been set for this game."


def test_run_game_without_init() -> None:
    ref = Referee()

    r = ref.run_game()
    assert r.is_error()
    assert r.error() == "must add players to this referee"
    assert ref.set_players(make_players(3)).is_ok()

    r = ref.run_game()
    assert r.is_error()
    assert r.error() == "must add a rule checker to this referee"
    ref.set_rule_checker(RuleChecker())

    r = ref.run_game()
    assert r.is_error()
    assert r.error() == "must add a tile iterator to this referee"
    ref.set_tile_iterator(deterministic_tile_iterator())

    r = ref.run_game()
    assert r.is_ok()


def test_get_tiles_error() -> None:
    ref = Referee()
    with pytest.raises(ValueError):
        ref._get_tiles(5)

def fast_function_test() -> int:
    return 3

def slow_function_test() -> int:
    time.sleep(5)
    return 2

def test_handle_player_timeout() -> None:
    ref = Referee()
    assert ref._handle_player_timeout("white", lambda: fast_function_test()) == 3
    assert ref._handle_player_timeout("black", lambda: slow_function_test()) == None
    assert ref._cheaters == {"black"}

    