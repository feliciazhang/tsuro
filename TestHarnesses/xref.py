"""
An implementation for the experimentation task in Assignment 7. Receives an array of 3-5 player names
from stdin where the players are in age-descending order. Outputs a json object containing the list of
cheaters (sorted lexicographically), and the list of lists representing the ranking of players in the
game, where each inner list is sorted lexicographically.
"""

from typing import List, cast

from Admin.referee import Referee, deterministic_tile_iterator
from Admin.game_observer import RefereeObserver
from Common.json_stream import StdinStdoutJSONStream
from Common.player_interface import PlayerInterface
from Common.rules import RuleChecker
from Player.first_s import FirstS
from Player.second_s import SecondS
from Player.third_s import ThirdS
from Player.player import Player


def main() -> None:
    """
    Create a referee with the given players, runs the game using first-s for each player,
    and outputs the results as a json object
    """
    json_stream = StdinStdoutJSONStream()
    player_names = cast(List[str], json_stream.receive_message().assert_value())
    players: List[PlayerInterface] = [Player(FirstS()) for _ in player_names]

    ref = Referee()
    colors = ref.set_players(players).assert_value()
    ref.set_rule_checker(RuleChecker())
    ref.set_tile_iterator(deterministic_tile_iterator())
    
    color_name_map = {color: name for color, name in zip(colors, player_names)}

    leaderboard, cheaters = ref.run_game().assert_value()

    json_stream.send_message(
        {
            "winners": [
                sorted([color_name_map[color] for color in rank])
                for rank in leaderboard
            ],
            "cheaters": sorted([color_name_map[color] for color in cheaters]),
        }
    )
  

if __name__ == "__main__":
    main()  
