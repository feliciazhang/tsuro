"""
Test harness for assignment 8. Receives an array of 3 to 20 player-specs in decreasing age order
and runs a tournament with those players.
"""
import sys, inspect
from importlib import util
from typing import List, Tuple, Set
from Admin.administrator import Administrator
from Common.json_stream import StdinStdoutJSONStream
from Common.player_interface import PlayerInterface
from Player.player import Player
from Common.tsuro_types import JSON
from Admin.bracket_strategy import SimpleBracketStrategy

# Creates a list of players in decreasing age order based on the provided player-specs
# Does not include players with the same name as a player older than them
# If an invalid strategy path is given, the player is not added to the tournament
def create_players(player_info: JSON)-> List[Tuple]:
  all_players = []
  for spec in player_info:
    if not any(spec["name"] == player[0] for player in all_players):
      Strat = None
      try:
        Strat = get_strategy_component(spec["strategy"])
      except Exception:
        continue
      if Strat != None:
        all_players.append((spec["name"], Player(Strat())))

  return all_players

# Dynamically loads the given strategy component based on the provided filepath
def get_strategy_component(strategy_path: str):
  module_spec = util.spec_from_file_location("strategy", strategy_path)
  module = util.module_from_spec(module_spec)
  module_spec.loader.exec_module(module)
  clsmembers = [c[0] for c in inspect.getmembers(module, inspect.isclass) if c[1].__module__ == "strategy"]
  strat_class = clsmembers[0]
  return getattr(module, strat_class)


# Runs a tournament with the given players and returns the results as a set of the winners' names
def run_tournament(players: List[Tuple]):
  admin = Administrator(SimpleBracketStrategy())
  player_ids_to_names = {}
  for player in players:
    r_player = admin.add_player(player[1])
    player_ids_to_names[r_player.assert_value()] = player[0]
  r_tournament = admin.run_tournament()
  winners = [sorted([player_ids_to_names[winner] for winner in winner_set]) for winner_set in r_tournament.assert_value()[0]]
  cheaters = [player_ids_to_names[cheater] for cheater in r_tournament.assert_value()[1]]
  return winners, cheaters

    
def main() -> None:
    json_stream = StdinStdoutJSONStream()
    player_info = json_stream.receive_message().assert_value()
    players = create_players(player_info)
    winners, cheaters = run_tournament(players)

    message = {
        "winners": winners,
        "cheaters": sorted(cheaters)
    } if len(cheaters) > 0 else {
        "winners": winners
    }
    json_stream.send_message(message)

if __name__ == "__main__":
    main()
