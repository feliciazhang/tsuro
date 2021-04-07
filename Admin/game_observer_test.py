# pylint: skip-file

import random
import time
from typing import Any, cast, List, Tuple
from unittest import mock

import pytest

from Common.board import Board
from Common.board_position import BoardPosition
from Common.board_state import BoardState
from Common.moves import InitialMove, IntermediateMove
from Common.tsuro_types import TileIndex
from Admin.game_observer import RefereeObserver
from Admin.referee import Referee, deterministic_tile_iterator
from Common.player_interface import PlayerInterface
from Common.result import Result, error, ok
from Common.rules import RuleChecker
from Common.tiles import PortID, Port, Tile, index_to_tile, tile_to_index, tile_pattern_to_tile
from Player.first_s import FirstS
from Player.second_s import SecondS
from Player.third_s import ThirdS
from Player.player import Player

t0_0 = tile_pattern_to_tile(0, 0)
t1_0 = tile_pattern_to_tile(1, 0)
t33_0 = tile_pattern_to_tile(33, 0)
t34_0 = tile_pattern_to_tile(34, 0)

board = Board()

INITIAL_MOVES_OFFERED = [("red", [t0_0, t1_0, t33_0]),
("blue", [t0_0, t1_0, t33_0]),
("black", [t0_0, t1_0, t33_0])]

INITIAL_MOVES_PLAYED = [("red", [t0_0, t1_0, t33_0], InitialMove(BoardPosition(1, 0), t0_0, Port.LeftTop, "red")),
("blue", [t0_0, t1_0, t33_0], InitialMove(BoardPosition(3, 0), t1_0, Port.LeftTop, "blue")),
("black", [t0_0, t1_0, t33_0], InitialMove(BoardPosition(5, 0), t33_0, Port.LeftTop, "black"))]

INTERMEDIATE_MOVES_OFFERED =[("red", [t0_0, t1_0]),
("blue", [t0_0, t33_0]),
("black", [t1_0, t33_0])]

INTERMEDIATE_MOVES_PLAYED = [("red", [t0_0, t1_0], IntermediateMove(t0_0, "red")),
("blue", [t0_0, t33_0], IntermediateMove(t0_0, "blue")),
("black", [t1_0, t33_0], IntermediateMove(t34_0, "black"))]

@pytest.mark.skip(  # type: ignore
    reason="Meant to be run manually for game observer graphically"
)
def test_run() -> None:
  referee_ob = RefereeObserver()

  referee_ob.players_added(["red", "blue", "black"])
  time.sleep(1)

  for i in range(0, len(INITIAL_MOVES_OFFERED)):
    
    referee_ob.initial_move_offered(INITIAL_MOVES_OFFERED[i][0], INITIAL_MOVES_OFFERED[i][1], board.get_board_state())
    
    time.sleep(1)

    referee_ob.initial_move_played(INITIAL_MOVES_PLAYED[i][0], INITIAL_MOVES_PLAYED[i][1], board.get_board_state(), INITIAL_MOVES_PLAYED[i][2])

    board.initial_move(INITIAL_MOVES_PLAYED[i][2])

    time.sleep(1)

  for i in range(0, len(INTERMEDIATE_MOVES_OFFERED)):
    
    referee_ob.intermediate_move_offered(INTERMEDIATE_MOVES_OFFERED[i][0], INTERMEDIATE_MOVES_OFFERED[i][1], board.get_board_state())
    
    time.sleep(1)

    referee_ob.intermediate_move_played(INTERMEDIATE_MOVES_PLAYED[i][0], INTERMEDIATE_MOVES_PLAYED[i][1], board.get_board_state(), INTERMEDIATE_MOVES_PLAYED[i][2], True)

    board.intermediate_move(INTERMEDIATE_MOVES_PLAYED[i][2])
    
    time.sleep(1)

  referee_ob.cheater_removed("red", board.get_board_state())
  referee_ob.cheater_removed("blue", board.get_board_state())
  
  referee_ob.game_result(([], set()))
  
def make_ref() -> Referee:
    ref = Referee()
    ref.set_rule_checker(RuleChecker())
    return ref


@pytest.mark.skip(  # type: ignore
    reason="Meant to be run manually for tournament observer graphically"
)
def test_2():
  ref = make_ref()
  ref_ob = RefereeObserver()
  ref.set_tile_iterator(deterministic_tile_iterator())
  ref.add_observer(ref_ob)
  player1 = Player(FirstS())
  player2 = Player(SecondS())
  player3 = Player(ThirdS())
  ref.set_players([player1, player2, player3])
  ref.run_game()
  


if __name__ == "__main__":
    test_2()
    while True:
      continue