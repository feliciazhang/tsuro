# Player Specification

This document serves to further assist in the implementation of a Tsuro game by providing an interface for Tsuro players that will be used by players competing in Tsuro tournaments. The implementation of this specification must be written in Python 3.6.8, use type hints, and pass `mypy --strict && pylint` without any errors. In addition, this specification provides some details about the internal organization of a player.

## Software Components

```python
from typing import List, Tuple
from Common.color import ColorString                  # See Planning/board.md
from Common.tiles import Tile, PortID                 # See Planning/board.md
from Common.board import BoardState                   # See Planning/board.md
from Common.board_position import BoardPosition       # See Planning/board.md
from Common.rules import RuleChecker                  # See Planning/rules.md
from Common.tsuro_types import GameResult             # See Planning/referee.md
from Player.observer_interface import PlayerObserver  # See PlayerObserver doc strings

class PlayerInterface:
    def set_color(self, color: ColorString) -> None:
        # Set the color of this Player
    def set_rule_checker(self, rule_checker: RuleChecker) -> None:
        # Set the rule checker that will be used by this game
    def generate_first_move(
        self, tiles: List[Tile], board_state: BoardState
    ) -> Tuple[BoardPosition, Tile, PortID]:
        # Generate the first move by choosing from the given list of tiles. Returns the move along with
        # the port that the player's token should be placed on. `set_color` and `set_rule_checker` will
        # be called prior to this method.
    def generate_move(self, tiles: List[Tile], board_state: BoardState) -> Tile:
        # Generate a move by choosing from the given list of tiles and returning the move. `set_color`,
        # `set_rule_checker`, and `generate_first_move` will be called prior to this method.
    def game_result(self, results: GameResult) -> None:
        # Called at the end of a game to provide the results of the game. See the definition of
        # GameResult for a description of this data type.
    def add_observer(self, observer: PlayerObserver) -> None:
        # Add the given player observer to this player. The player must support adding multiple player 
        # observers and sending events to all of the added observers. See the definition of the
        # PlayerObserver interface for information on the observer methods.
```

## Internal Organization

### Initialization Process

The `PlayerInterface` will be initialized by calling `set_color(ColorString)`. This will specify the color that the player will be during the game. It will then be further initialized by calling `set_rule_checker(RuleChecker)`. This allows the referee that is running the game to provider a rule checker to the player. This allows players to check the validity of their moves prior to returning them to the referee.

The final step of the initialization process is when the referee calls the `generate_first_move(List[Tile], BoardState)` method. The player must return an initial move (represented by a board position, a chosen tile, and a port ID) to the referee. The player may use the methods on the board state in order to determine which tiles are occupied and it may use the rule checker to validate any chosen moves. If other players went before this player, that will also be viewable via the board state.

### Steady State

The steady state operation of a player will consist of a series of calls to the `generate_move(List[Tile], BoardState)` method. The player may use the rule checker and the board state in order to strategize and attempt to determine a "good" move. Through this, the player will be able to view the state of the board along with the locations of the other living players. It is recommended that the player validate all moves with the rule checker prior to returning them.

### Shutdown Process

At the end of a game if a player has not been terminated the referee will call `game_result(GameResult)` in order to provide the results of the game to the player strategies.