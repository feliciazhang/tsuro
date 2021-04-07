# Game Observer Specification

This document serves to further assist in the implementation of a Tsuro game by providing an interface for Tsuro game observers that will be used by anyone who wants to observe an individual Tsuro game. The implementation of this specification must be written in Python 3.6.8, use type hints, and pass `mypy --strict && pylint` without any errors.

## Game Observer Purpose

This specification describes how the observer design pattern could be applied to designing an observer such that someone could observe an individual Tsuro game. See Planning/referee.md for a description of the software component that runs a Tsuro game. The observer described below can be thought of as a Referee observer. 

## Software Components

```python
from typing import List
from Common.tsuro_types import GameResult
from Common.color import ColorString
from Common.moves import InitialMove, IntermediateMove
from Common.board import BoardState                                 # See Planning/board.md
from Common.tiles import Tile                                       # See Planning/board.md

class RefereeObserver:
    def players_added(self, players: List[ColorString]) -> None:
        """
        An observer method that is called to describe when players are added to the game. The list is
        ordered by age descending.

        :param players:         The list of player avatars that were added to the game
        """

    def game_completed(self, leaderboard: GameResult) -> None:
        """
        An observer method that is called at the end of game to deliver the game result to the referee
        observer.
        
        :param leaderboard:     The results of the completed game
        """

    def initial_move_offered(
        self, player: ColorString, tiles: List[Tile], board_state: BoardState
    ) -> None:
        """
        An observer method that is called to describe when a player is prompted for an initial move and
        the data that is given to them when they are prompted for an initial move.

        :param player:          The player who is being asked for a move
        :param tiles:           The list of tiles that the player is allowed to choose between
        :param board_state:     The board state that the player is playing against
        """

    def initial_move_played(
        self, player: ColorString, tiles: List[Tile], board_state: BoardState, move: InitialMove
    ) -> None:
        """
        An observer method that is called to describe when a player returns an initial move to be placed

        :param player:          The player who is being asked for a move
        :param tiles:           The list of tiles that the player is allowed to choose between
        :param board_state:     The board state that the player is playing against
        :param move:            The initial move that the player placed on the board
        """

    def intermediate_move_offered(
        self, player: ColorString, tiles: List[Tile], board_state: BoardState
    ) -> None:
        """
        An observer method that is called to describe when a player is prompted for an intermediate move
        and the data that is given to them when they are prompted for an intermediate move.

        :param player:          The player who is being asked for a move
        :param tiles:           The list of tiles that the player is allowed to choose between
        :param board_state:     The board state that the player is playing against
        """

    def intermediate_move_played(
        self, player: ColorString, tiles: List[Tile], board_state: BoardState, move: IntermediateMove
    ) -> None:
        """
        An observer method that is called to describe when a player returns an intermediate move to be
        placed.

        :param player:          The player who is being asked for a move
        :param tiles:           The list of tiles that the player is allowed to choose between
        :param board_state:     The board state that the player is playing against
        :param move:            The intermediate move that the player placed on the board
        """

    def cheater_removed(self, player: ColorString) -> None:
        """
        An observer method that is called to describe when a player is removed for cheating.

        :param player:          The player who was removed for cheating
        """

    def player_eliminated(self, player: ColorString) -> None:
        """
        An observer method that is called to describe when a player is eliminated due to moving off of
        the board or being killed by a loop

        :param player           The player who was eliminated when moved off the board
        """

    def game_result(self, game_result: GameResult) -> None:
        """
        An observer method that is called when the game of Tsuro is complete.

        :param game_result:     The game results
        """
```

## Changes needed in referee

When adding game observers, there will need to be a few other modifications to the referee. Some of these include:

- Adding the `add_observer` method. The `add_observer` method should support adding multiple observers, as well as support adding observers in the middle of the game.

- The referee should call all methods in each the RefereeObserver provided to it at the appropriate time. The referee should also silence all exceptions or errors thrown or returned by the observers.

## Notes

Due to limitations of mypy's typing system, we are not using a generalized Observer interface as one might see in other languages (eg Java). Instead, we define our observer interfaces explicitly for each time we use the observer design pattern. This allows us to write python code that takes full advantage of mypy's static typechecking abilities which we believe significantly improves the maintainability and reliability of our codebase.