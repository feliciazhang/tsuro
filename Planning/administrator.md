# Tsuro Administrator Specification

This document serves to further assist in the implementation of a Tsuro game by providing an interface for Tsuro administrators that will be used to run Tsuro tournaments. The implementation of this specification must be written in Python 3.6.8, use type hints, and pass `mypy --strict && pylint` without any errors.

## Terminology

A Tsuro game is run by a referee (see referee.md). Since a Tsuro game has a maximum of five players, a Tsuro game cannot rank more than 5 players against each other. A Tsuro tournament consists of multiple Tsuro games where a given player may compete multiple times in order to determine a ranking of players across many games. Tsuro tournaments are divided into multiple rounds where a round consists of multiple Tsuro games. At the end of a round, one or more players are eliminated from a Tournament which determines their position in a tournament leaderboard. 

## Software Components

```python
from typing import List, Set, Tuple, NewType
from Common.result import Result
from Common.tsuro_types import GameResult
from Common.player_interface import PlayerInterface   # See Planning/player.md

# Represents an ID that uniquely identifies a player within the context of an admin
PlayerID = NewType("PlayerID", str)
# Represents the age of a player
PlayerAge = NewType("PlayerAge", int)
# Represents a leaderboard for a Tsuro tournament. The first element of the list is the set of
# players that tied for first place in the tournament, the second element is the set of players
# that tied for second place, and so on.
TournamentLeaderboard = List[Set[PlayerID]]
# Represents the final outcome of running a Tsuro tournament. A tuple that contains a leaderboard and a set.
# The leaderboard is the people who won the game. The set is the set of cheaters. Every person who competed
# in a tournament is guaranteed to occur in the leaderboard exactly once.
TournamentResult = Tuple[TournamentLeaderboard, Set[PlayerID]]

class Administrator:
    def add_player(self, player: PlayerInterface, player_age: int) -> Result[PlayerID]:
        # Add the given player to this Tsuro game administrator. All players must be added prior to
        # calling run_tournament(). Returns a result containing a unique ID that can be used to refer to
        # the player in the future. 
    def run_tournament(self, bracket_strategy: 'BracketStrategy') -> Result[TournamentLeaderboard]:
        # Start the current tournament and run it to completion. All players must have been added to the
        # administrator prior to calling run_tournament. The given bracket strategy is used to define
        # how individual games within a tournament are paired up and how players are eliminated based
        # off of GameResults. Creates a referee for each game and passes it a rule checker (that the
        # administrator creates) to define the rules for the tournament. Returns a result containing the
        # tournament leaderboard.

class BracketStrategy:
    def bucket_players(self, live_players: Set[Tuple[PlayerID, PlayerAge]]) -> Result[Set[Set[PlayerID]]]:
        # Bucket the given set of player IDs into a set of buckets of player IDs. For example, given
        # {'A', 'B', 'C', 'D', 'E', 'F'} this method could return
        # {{'A', 'B', 'C', 'D', 'E'}, {'B', 'C', 'D', 'E'}}. This splits a set of alive players into
        # individual games that can be run by a referee (see `Planning/referee.md` for information on
        # how this would work). Each set in the return value must have between 3 and 5 player IDs in it.
        # A number of different strategies could be possible here ranging from naive to complex
        # strategies that allow double or triple elimination. May return an error if this bracket
        # strategy does not support bucketing a set with the given number of players. 

    def eliminate_players(
        self, live_players: Set[PlayerID], game_results: List[GameResult]
    ) -> Result[Set[PlayerID]]:
        # Given the set of live players and the list of game results returns the set of players which
        # should be eliminated from the tournament. For example, a double elimination bracket strategy
        # may count the number of times that a player lost and after two times return them. In addition,
        # note that a GameResult contains the set of cheaters in a specific game thereby making it
        # possible for a BracketStrategy to decide elimination strategies based off of whether someone
        # cheated or not. 
```
