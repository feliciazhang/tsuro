# Tournament Observer Specification

This document serves to further assist in the implementation of a Tsuro game by providing an interface for Tsuro tournament observers that will be used by anyone who wants to observe a Tsuro tournament. The implementation of this specification must be written in Python 3.6.8, use type hints, and pass `mypy --strict && pylint` without any errors.

## Tournament Observer Purpose

This specification describes how the observer design pattern could be applied to designing an observer such that someone could observe an entire Tsuro tournament. See Planning/administrator.md for a description of the software component that runs a Tsuro tournament. The observer described below can be thought of as an Administrator observer. 

## Software Components

```python
from typing import Set
from Common.administrator import PlayerID, TournamentLeaderboard    # See Planning/administrator.md

class AdministratorObserver:
    def player_added(self, player_id: PlayerID, player_age: int) -> None:
        """
        An observer method that is called to describe when a player is added to the game. Provides the
        player ID that the player was assigned by the administrator. The player's join time is used to
        determine their age which determines the order in which they play in individual Tsuro games.

        :param player_id:   The player ID of the added player
        :param player_age:  The age of the added player
        """
        
    def games_created(self, games: Set[Set[PlayerID]]) -> None:
        """
        An observer method that is called to describe when a set of games is created by the
        BracketStrategy. A game is represented as a set of 3-5 player IDs that will play against each
        other in a single game of Tsuro. Thus, multiple games are represented as a set of games. This
        observer method is called prior to the individual game being executed by a referee.
        
        :param games:  The set of games that have been created
        """
        
    def game_completed(self, game: Set[PlayerID], game_result: TournamentLeaderboard) -> None:
        """
        An observer method that is called to describe when an individual Tsuro game is completed.
        Provides the players that played in the game and the game result. Note that the game_result is
        of type TournamentLeaderboard so that is uses the same player IDs that the observer is provided.
        
        :param game:        The set of players that played in the game
        :param results:     The results of the individual game
        """
        
    def players_eliminated(self, eliminated_players: Set[PlayerID]) -> None:
        """
        An observer method that is called to describe when players are eliminated from a Tsuro
        tournament by the administrator's bracket strategy. To be precise, this type of elimination is
        based off of player's performance in individual Tsuro games. If a player is removed for
        cheating, this method is not called. It is guaranteed that a player can only be eliminated a
        single time.
        
        :param eliminated_players:  The set of players eliminated from the tournament
        """
        
    def player_cheated(self, player: PlayerID) -> None:
        """
        An observer method that is called to describe when a player is removed from the tournament for
        cheating.
        
        :param player:  The player ID of the player that attempted to cheat
        """
        
    def tournament_completed(self, leaderboard: TournamentLeaderboard) -> None:
        """
        An observer method that is called to describe when a Tsuro tournament is completed. Provides
        the complete leaderboard of the completed Tsuro tournament.
        
        :param leaderboard:     The leaderboard of the completed Tsuro tournament
        """
```

## Notes

- In the future, if a tournament observer wanted to observe an individual game this could be done by correlating player IDs with colors used internally in a game. This data is stored inside of a tournament but could easily be exposed if this feature was needed.

- Due to limitations of mypy's typing system, we are not using a generalized Observer interface as one might see in other languages (eg Java). Instead, we define our observer interfaces explicitly for each time we use the observer design pattern. This allows us to write python code that takes full advantage of mypy's static typechecking abilities which we believe significantly improves the maintainability and reliability of our codebase.
