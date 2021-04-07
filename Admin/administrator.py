"""
A Tsuro administrator capable of running many Tsuro games in a tournament structure.

In order to implement this, we had to change:
* The player interface and players in order to add a `Player.notify_won_tournament()` method.
  This method was not required per the earlier specifications but was required per assignment 7.
* Changed the bracket strategy from the one in the specification to include player ages so as
  to make it possible for the bracket strategy to bucket players based off of age.
"""
import time
from typing import TYPE_CHECKING, FrozenSet, List, NewType, Optional, Set, Tuple
from uuid import uuid4

from Admin.referee import Referee, deterministic_tile_iterator
from Common.color import ColorString
from Common.player_interface import PlayerInterface
from Common.result import Result, error, ok
from Common.rules import RuleChecker
from Common.tsuro_types import GameResult
from Common.util import silenced_object, timeout
from Common.validation import validate_types


if TYPE_CHECKING:
    # Prevent an import loop by only importing if we are type checking
    from Admin.bracket_strategy import (  # pylint: disable=ungrouped-imports
        BracketStrategy,
    )  # isort:skip

TIMEOUT = 3

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
    """
    A Tsuro administrator capable of running a Tsuro tournament containing many players.
    """

    players: List[Tuple[PlayerInterface, PlayerID, PlayerAge]]
    bracket_strategy: "BracketStrategy"

    def __init__(self, bracket_strategy: "BracketStrategy") -> None:
        """
        Make a new Tsuro administrator with a default empty list of players

        :param bracket_strategy:    A bracket strategy that defines how players are paired up for individual games
                                    and how players are eliminated after each round of completed games
        """
        self.players = []
        self.cheaters = []
        self.bracket_strategy = bracket_strategy
        self._observers = []
    
    @validate_types
    def add_observer(self, observer):
        self._observers.append(observer)

    @validate_types
    def add_player(
        self, player: PlayerInterface, player_age: Optional[PlayerAge] = None
    ) -> Result[PlayerID]:
        """
        Add the given player to this Tsuro game administrator. All players must be added prior to
        calling run_tournament(). Returns a result containing a unique ID that can be used to refer to
        the player in the future.

        :param player:          The automated player to add to this tournament
        :param player_age:      The age of the player that is added to the tournament. Defaults to time.time()
        :return:                The ID of the added player
        """
        if player_age is None:
            player_age = PlayerAge(int(time.time() * 100000))
        player_id = PlayerID(str(uuid4()))
        self.players.append((silenced_object(player), player_id, player_age))

        for observer in self._observers:
            observer.player_added(player_id)
        return ok(player_id)

    #  -> Result[Tuple[List[Set[PlayerID]], Set[PlayerID]]]
    @validate_types
    def run_tournament(self) -> Result[TournamentResult]:
        """
        Start the current tournament and run it to completion. All players must have been added to the
        administrator prior to calling run_tournament.

        Note that this method may only be called once per Administrator

        :return:    A result containing the set of players that won the tournament
        """
        while len(self.players) >= 3:
            r = self._run_round()
            if r.is_error():
                return error(r.error())

            maybe_results = r.value()
            if maybe_results:
                self._notify_winners(list(maybe_results[0][0]))
                for observer in self._observers:
                    observer.tournament_completed(maybe_results)
                return ok(maybe_results)
        return self._run_not_enough_players()

    def _run_not_enough_players(self) -> Result[TournamentResult]:
        """
        If there is an insufficient number of players to run a game for the
        tournament, all players are winners.
        """
        winners = [pid for player, pid, age in self.players]
        self._notify_winners(winners)
         
        for observer in self._observers:
            observer.tournament_completed(([winners], set(self.cheaters)))

        return ok(([winners], set(self.cheaters)))

    def _run_round(self) -> Result[Optional[TournamentResult]]:
        """
        Run a single round of a Tsuro tournament and update self.players based off of
        the results of the tournament.

        :return:    If the tournament is over, return the Results of the single
        game, otherwise return a Result containing None. 
        """
        games_r = self.bracket_strategy.bucket_players(
            set((player_id, player_age) for player, player_id, player_age in self.players))
        if games_r.is_error(): return error(games_r.error())

        for observer in self._observers: observer.games_created(games_r.value())

        if len(games_r.value()) == 1:
            return self._run_last_game(games_r.value())
        else:  
            game_results_r = self._run_games(games_r.value())
            if game_results_r.is_error(): return error(game_results_r.error())

            self._handle_eliminated_players(game_results_r)
            
            for game_result in game_results_r.value():
                winners, game_cheaters = game_result
                self.cheaters.extend(game_cheaters)

            return ok(None)
    
    def _handle_eliminated_players(self, game_results_r):
        """
        Removes losers from the list of current players given the game results
        from a single round.
        :param game_results_r: The list of game results
        :return: An error if there is an error in the result.
        """
        eliminated_r = self.bracket_strategy.eliminate_players(
                set(player_id for player, player_id, player_age in self.players),
                game_results_r.value(),
        )
        
        if eliminated_r.is_error(): return error(eliminated_r.error())
      
        self.players = [
            (player, player_id, player_age)
            for player, player_id, player_age in self.players
            if player_id not in eliminated_r.value()
        ]

        for observer in self._observers: observer.players_eliminated(eliminated_r.value())
        

    def _run_last_game(self, game: Set[FrozenSet[PlayerID]]) -> Result[TournamentResult]:
        """
        Handles the results of the last game of the tournament.
        
        :param game:    A set of games, represented by sets of player IDs, 
        which is length 1 becaues it is the last game.
        :return:    The winners and cheaters of the tournament after the game is complete. 
        """
        game_results_r = self._run_games(game)
      
        if game_results_r.is_error(): 
            return error(game_results_r.error())

        winners = game_results_r.value()[0][0]
        cheaters = game_results_r.value()[0][1]
        self.cheaters.extend(cheaters)
        return ok((winners, set(self.cheaters)))
    
    def _run_games(
        self, games: Set[FrozenSet[PlayerID]]
    ) -> Result[List[TournamentResult]]:
        """
        Run a series of games and return the results of the games

        :param games:   A set of games represented as a set of sets where the inner sets are the players that should play in a given game
        :return:        A Result containing a list of game results
        """
        tournament_results = []
        for player_ids in games:
            ref = self._initialize_ref()
            
            sorted_player_ids = list(sorted(player_ids, key=self._get_age_by_id))
            players = [self._get_player_by_id(player_id) for player_id in sorted_player_ids]
            
            colors_r = ref.set_players(players)
            if colors_r.is_error(): return error(colors_r.error())

            for observer in self._observers: observer.game_started(player_ids)

            game_r = ref.run_game()
            if game_r.is_error(): return error(game_r.error())
        
            for observer in self._observers: observer.game_completed(player_ids, game_r.value())

            tournament_results.append(translate_color_to_pids(game_r.value(), sorted_player_ids, colors_r.value()))

        return ok(tournament_results)

    def _initialize_ref(self) -> Referee:
        """
        Sets up a ref to run a game.
        """
        ref = Referee()
        ref.set_rule_checker(RuleChecker())
        ref.set_tile_iterator(deterministic_tile_iterator())
        return ref

    @validate_types
    def _notify_winners(self, winners: List[PlayerID]) -> None:
        """
        Notify everyone who did not cheat in the tournament whether or not they won.
        If the player fails while being notified that they won, just continue.
        :param winners:     The set of people who won the tournament
        """
        for player in self.players:
            if player[1] not in self.cheaters:
                try:
                    with timeout(TIMEOUT):
                        player[0].notify_won_tournament(player[1] in winners)
                except:
                    continue


    @validate_types
    def _get_player_by_id(self, player_id: PlayerID) -> PlayerInterface:
        """
        Get the player associated with the given player ID

        :param player_id:   The ID of the player
        :return:            The automated player
        """
        for player, pid, age in self.players:
            if pid == player_id:
                return player
        raise ValueError(
            f"Broken Constraint: Failed to find player_id in self.players that matches {player_id}"
        )

    @validate_types
    def _get_age_by_id(self, player_id: PlayerID) -> PlayerAge:
        """
        Get the player age associated with the given player ID

        :param player_id:   The ID of the player
        :return:            The age of the player
        """
        for player, pid, age in self.players:
            if pid == player_id:
                return age
        raise ValueError(
            f"Broken Constraint: Failed to find player_id in self.players that matches {player_id}"
        )


@validate_types
def translate_color_to_pids(
    game_result: GameResult, player_ids: List[PlayerID], colors: List[ColorString]
) -> TournamentResult:
    """
    Translate the given game result (which refers to players by their color) to a tournament leaderboard (which refers
    to players by their player ID).

    :param game_result:     The game result to translate to a tournament leaderboard
    :param player_ids:      The list of player IDs in the same order as the list of colors
    :param colors:          The list of colors in the same order as the list of player IDs
    :return:                A tournament leaderboard that represents the same data as the given game result
    """

    def color_to_pid(color: ColorString) -> PlayerID:
        for idx, other_color in enumerate(colors):
            if other_color == color:
                return player_ids[idx]
        raise ValueError(
            f"Broken Constraint: Failed to find color in colors that matches {color}"
        )

    assert len(player_ids) == len(colors)
    winners, cheaters = game_result
    new_cheaters = set(color_to_pid(color) for color in cheaters)
    new_winners = []
    for item in winners:
        new_winners.append(set(color_to_pid(color) for color in item))

    return new_winners, new_cheaters
