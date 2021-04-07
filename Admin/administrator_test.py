# pylint: skip-file
from typing import List, TypeVar, cast
from unittest.mock import Mock, call
import time
import pytest

from Admin.administrator import (
    Administrator,
    PlayerID,
    TournamentResult,
    translate_color_to_pids,
)
from Admin.bracket_strategy import SimpleBracketStrategy
from Admin.referee_test import CrashingPlayer, make_players
from Common.color import ColorString
from Common.result import error
from Common.tsuro_types import GameResult
from Common.util import timeout
from Common.validation import disable_validation
from Player.first_s import FirstS
from Player.player import Player
from Player.second_s import SecondS
from Admin.tournament_observer import TournamentObserver


def test_admin_2_first_s() -> None:
    admin = Administrator(SimpleBracketStrategy())
    pid_to_idx = {}
    for idx, player in enumerate(make_players(2)):
        pid_r = admin.add_player(player)
        assert pid_r.is_ok()
        pid_to_idx[pid_r.value()] = idx
    winners_r = admin.run_tournament()
    assert winners_r.is_ok()
    real_winners = winners_r.value()[0][0]
    assert set([pid_to_idx[pid] for pid in real_winners]) == {0, 1}


def test_admin_5_first_s() -> None:
    admin = Administrator(SimpleBracketStrategy())
    pid_to_idx = {}
    for idx, player in enumerate(make_players(5)):
        pid_r = admin.add_player(player)
        assert pid_r.is_ok()
        pid_to_idx[pid_r.value()] = idx
    winners_r = admin.run_tournament()
    assert winners_r.is_ok()
    real_winners = winners_r.value()[0][0]
    assert set([pid_to_idx[pid] for pid in real_winners]) == {0}


@disable_validation  # Our validation is upset about mocks
def test_admin_5_second_s() -> None:
    admin = Administrator(SimpleBracketStrategy())
    pid_to_idx = {}
    players = []
    for idx in range(5):
        player = Mock(wraps=Player(SecondS()))
        players.append(player)
        pid_r = admin.add_player(player)
        assert pid_r.is_ok()
        pid_to_idx[pid_r.value()] = idx
    winners_r = admin.run_tournament()
    assert winners_r.is_ok()
    real_winners = winners_r.value()[0][0]
    assert set([pid_to_idx[pid] for pid in real_winners]) == {0, 2}
    assert players[0].notify_won_tournament.call_args_list == [call(True)]
    assert players[1].notify_won_tournament.call_args_list == [call(False)]
    assert players[2].notify_won_tournament.call_args_list == [call(True)]
    assert players[3].notify_won_tournament.call_args_list == [call(False)]
    assert players[4].notify_won_tournament.call_args_list == [call(False)]


def test_admin_10_second_s() -> None:

    # Assert that it runs in a reasonable amount of time
    with timeout(seconds=10):
        admin = Administrator(SimpleBracketStrategy())
        pid_to_idx = {}
        for idx in range(10):
            pid_r = admin.add_player(Player(SecondS()))
            assert pid_r.is_ok()
            pid_to_idx[pid_r.value()] = idx
        winners_r = admin.run_tournament()
        assert winners_r.is_ok()
        real_winners = winners_r.value()[0][0]
        assert len(real_winners)
        assert set([pid_to_idx[pid] for pid in real_winners]) == {1, 5}

@pytest.mark.skip(  # type: ignore
    reason="Meant to be run manually for tournament observer graphically"
)
def test_admin_by_function() -> None:
    tobs = TournamentObserver()
    admin = Administrator(SimpleBracketStrategy())
    admin.add_observer(tobs)

    pid_to_idx = {}
    for idx in range(20):
        pid_r = admin.add_player(Player(SecondS()))
        assert pid_r.is_ok()
        pid_to_idx[pid_r.value()] = idx
        time.sleep(0.1)
    
    admin.run_tournament()



def test_admin_crashing_player() -> None:
    admin = Administrator(SimpleBracketStrategy())

    cp_exception_init = CrashingPlayer(True, True)
    assert admin.add_player(cp_exception_init).is_ok()
    cp_error_init = CrashingPlayer(False, True)
    assert admin.add_player(cp_error_init).is_ok()
    cp_exception_inter = CrashingPlayer(True, False)
    assert admin.add_player(cp_exception_inter).is_ok()
    cp_error_inter = CrashingPlayer(False, False)
    assert admin.add_player(cp_error_inter).is_ok()
    p = Player(FirstS())
    r = admin.add_player(p)
    assert r.is_ok()
    real_player_pid = r.value()

    winners_r = admin.run_tournament()
    assert winners_r.is_ok()
    real_winners = winners_r.value()[0][0]
    assert real_winners == {real_player_pid}


def test_translate_color_to_pids() -> None:
    gr: GameResult = ([{"red"}, set(), {"blue"}, {"black"}], {"white", "green"})
    colors: List[ColorString] = ["red", "blue", "black", "white", "green"]
    ids = [PlayerID("a"), PlayerID("b"), PlayerID("c"), PlayerID("d"), PlayerID("e")]

    tr = translate_color_to_pids(gr, ids, colors)
    assert tr == (
        [{PlayerID("a")}, set(), {PlayerID("b")}, {PlayerID("c")}],
        {PlayerID("d"), PlayerID("e")},
    )

if __name__ == "__main__":
    test_admin_by_function()