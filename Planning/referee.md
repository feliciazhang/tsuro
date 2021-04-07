# Referee Specification

This document serves to further assist in the implementation of a Tsuro game by providing an interface for Tsuro referees that will be used to run Tsuro tournaments. The implementation of this specification must be written in Python 3.6.8, use type hints, and pass `mypy --strict && pylint` without any errors.

## Software Components

```python
from typing import Iterator, List
from Common.color import ColorString
from Common.player_interface import PlayerInterface
from Common.result import Result
from Common.rules import RuleChecker
from Common.tiles import Tile
from Common.tsuro_types import GameResult
from Admin.observer_interface import RefereeObserver  # See RefereeObserver doc strings

class Referee:
    def set_players(self, players: List[PlayerInterface]) -> Result[List[ColorString]]:
        """
        Add the given players (ordered by age, decreasing) to the game. Ties for age can be represented in either order.
        Returns an error if `len(players)` is greater than 5 or less than 3, or if the method has already been called.

        :param players: Players for this referee to use in a game.
        :return:        The list of colors that will be assigned to those players.
        """

    def set_rule_checker(self, rule_checker: RuleChecker) -> None:
        """
        Set the rule checker to be used by this referee. Must be called prior to calling run_game().

        :param rule_checker: The rule checker that the referee should use.
        """

    def set_tile_iterator(self, tile_iterator: Iterator[Tile]) -> None:
        """
        Set the iterator of tiles to be used by this referee. Must be infinite.

        :param tile_iterator: The infinite tile iterator to be used by this referee.
        """

    def run_game(self) -> Result[GameResult]:
        """
        Run an entire game of Tsuro with the players that have been added to this referee. Returns the result
        of the game.

        A list of players, a rule checker, and a tile iterator must have already been set on this referee
        prior to calling run_game.

        :return: The GameResult at the end of the game, or an error if something goes wrong.
        """

    def add_observer(self, observer: RefereeObserver) -> None:
        """
        Add the given game observer to this referee. The referee must support adding multiple player observers and sending events to all of the added observers. See the definition of the RefereeObserver interface for information on the observer methods.

        :param observer: A game observer to add to this interface that will receive all events
        """
```

## Internal Organization

Whenever interacting with players, the referee will catch all exceptions that may be thrown by players and ensure that they do not bubble up further. This will ensure that players will not crash the game if they crash themselves.

### Initialization Process

The `Referee` will be initialized by calling `set_players(List[PlayerInterface])`. This will add the players to the referee, ordered by age decreasing, storing the players along with their assigned colors. The method must be called with 3-5 players inclusive. The `set_players` method will be responsible for verifying this and rejecting invalid additions. In the initialization process, the `set_rule_checker` and `set_tile_iterator` methods must also be called. The referee will use the provided rule checker and tile iterator for the game.

### Steady State

The steady state operation of a referee will be initiated by calling the `run_game()` method of the referee. Once run game has been called, it is illegal to attempt to add any more players, set the rule checker, or set the tile iterator to the referee. Run game will create a new Board (see Planning/board.md) and then go through the initialization phase for players as described in Planning/player.md. This consists of querying each player for their initial move. After receiving a move from a player, the referee will use a rule checker to validate the move prior to applying it to the board. After this, it will then start the main game loop, which will consistently query players for their next intermediate move. These moves will also be validated via the rule checker prior to applying them to the board. After each move, the game loop will keep track of any players that exited the board (via adding an observer to the board) and build up the `GameResult`. Once all players have exited the board, it will enter the shutdown process.

### Shutdown Process

During the shutdown process, `run_game()` will pass the `GameResult` to each player as defined in Planning/player.md. This will complete the shut down phase of each player. After that, `run_game()` will return the game result describing what happened during the game. At this point, the referee has completed shutdown. After this point, it is illegal to call any methods on the shut-down referee instance.
