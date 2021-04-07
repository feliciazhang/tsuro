# pylint: skip-file

import time
import pytest

from Admin.tournament_observer import TournamentObserver

PLAYERS = ["a", "b", "c", "d", "e", "z", "f", "g", "h", "i", "j", "k", "l", "m"]

TEST_ROUNDS = [
    {
        "create": set([frozenset(["a", "b", "c", "d", "e"]), frozenset(["z", "f", "g", "h", "i"]), frozenset(["j", "k", "l", "m"])]),
        "games": [
            [{"a", "b", "c", "d", "e"}, ({"a", "b", "c", "d", "e"}, {"winners": [["a"]], "cheaters": ["d", "e"]})],
            [{"z", "f", "g", "h", "i"}, ({"z", "f", "g", "h", "i"}, {"winners": [["z"]], "cheaters": ["h"]})],
            [{"j", "k", "l", "m"}, ({"j", "k", "l", "m"}, {"winners": [["k"]], "cheaters": []})]
        ]
    },
    {
        "create": set([frozenset(["a", "z", "k"])]),
        "games": [
            [{"a", "z", "k"}, ({"a", "z", "k"}, {"winners": [["a"],["z"]], "cheaters": ["k"]})]
        ]
    }
]

@pytest.mark.skip(  # type: ignore
    reason="Meant to be run manually for testing purposes. Displays an animated Tournament Observer output to the user."
    "Run manually via: `python3.6 -m Admin.tournament_observer_test`"
)
def test_run() -> None:
    """
    Test function to run the graphical tournament observer locally with some test data. Meant to be run
    locally and inspected in order to ensure the GUI is working properly.
    :return:    None
    """

    gto = TournamentObserver()
    # Add all players
    for p in PLAYERS:
        gto.player_added(p)
        # time.sleep(0.5)
    
    for round in TEST_ROUNDS:
        gto.games_created(round["create"])
        time.sleep(0.5)
        for game in round["games"]:
            gto.game_started(game[0])
            time.sleep(0.5)
            gto.game_completed(game[1][0], game[1][1])
            gto.players_eliminated(game[1][1]["cheaters"])
            time.sleep(0.5)
    gto.tournament_completed([[["a"], ["z"]], ["k"]])



if __name__ == "__main__":
    test_run()
