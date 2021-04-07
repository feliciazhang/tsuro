"""
A module that holds an interface and an implementation of a bracket strategy that calculates how to divide a
set of Tsuro players into individual games of Tsuro for the purpose of running a Tournmanet. A bracket strategy
is also responsible for determining when players should be eliminated from a tournament.
"""
from typing import FrozenSet, List, Set, Tuple

from Admin.administrator import PlayerAge, PlayerID, TournamentResult
from Common.result import Result, error, ok
from Common.validation import validate_types


class BracketStrategy:
    # pylint: disable=no-self-use, unused-argument
    """
    An interface for bracket strategies that determine how to divide Tsuro players into individual games and how to
    eliminate players at the end of a round of games.
    """

    def bucket_players(
        self, live_players: Set[Tuple[PlayerID, PlayerAge]]
    ) -> Result[Set[FrozenSet[PlayerID]]]:
        """
        Bucket the given set of player IDs into a set of buckets of player IDs.

        For example, given {'A', 'B', 'C', 'D', 'E', 'F'} this method could return
        {{'A', 'B', 'C', 'D', 'E'}, {'B', 'C', 'D', 'E', 'F'}}. This splits a set of alive players into
        individual games that can be run by a referee.

        Each set in the return value must have between 3 and 5 player IDs in it. A number of
        different strategies could be possible here ranging from naive to complex strategies
        that allow double or triple elimination. May return an error if this bracket strategy
        does not support bucketing a set with the given number of players.

        :param live_players:    The set of live players represented by their player IDs and age
        :return:                A set of sets where each set represents the players that will play in a game
        """
        return error("BracketStrategy.bucket_players is not implemented!")

    def eliminate_players(
        self, live_players: Set[PlayerID], game_results: List[TournamentResult]
    ) -> Result[Set[PlayerID]]:
        """
        Given the set of live players and the list of game results returns the set of players which
        should be eliminated from the tournament. For example, a double elimination bracket strategy
        may count the number of times that a player lost and after two times return them. In addition,
        note that a GameResult contains the set of cheaters in a specific game thereby making it
        possible for a BracketStrategy to decide elimination strategies based off of whether someone
        cheated or not.

        :param live_players:    The set of live players represented by their player IDs
        :param game_results:    A set of game results for each of the games run by the administrator
        :return:                A set of the players that should be eliminated from the game
        """
        return error("BracketStrategy.eliminate_players is not implemented!")


class SimpleBracketStrategy(BracketStrategy):
    # pylint: disable=no-self-use
    """
    A simple deterministic bracket strategy that determines how to divide Tsuro players into individual games and how to
    eliminate players at the end of a round of games. Divides players into games in a greedy manner in order of age and
    eliminates players via single elimination.
    """

    @validate_types
    def bucket_players(
        self, live_players: Set[Tuple[PlayerID, PlayerAge]]
    ) -> Result[Set[FrozenSet[PlayerID]]]:
        """
        Bucket the given set of player IDs into a set of buckets of player IDs in a simple deterministic
        manner. Players are first sorted by their age (ascending order) and then split into groups of
        five in order of the sorted list. If one player remains, it uses the last 6 players to form two
        groups of three. If two players remain, it uses the last 7 players to form a group of 4 and 3. If
        three players remain, it uses the last 8 players to form a group of 5 and 3. If four players remain,
        it uses the last 9 players to form a group of 5 and 4.

        For example, given {'A', 'B', 'C', 'D', 'E', 'F'} this method would return
        {{'A', 'B', 'C'}, {'D', 'E', 'F'}}.

        :param live_players:    The set of live players represented by their player IDs and age
        :return:                A set of sets where each set represents the players that will play in a game
        """
        if len(live_players) < 3:
            return error(
                f"cannot create a Tsuro tournament with less than 3 players (tried {len(live_players)})"
            )
        sorted_players = sorted(live_players, key=lambda x: x[1])
        return ok(self._bucket_players(sorted_players))

    def _bucket_players(
        self, players: List[Tuple[PlayerID, PlayerAge]]
    ) -> Set[FrozenSet[PlayerID]]:
        """
        _bucket_players() serves as a helper for bucket_players(). It performs the function defined
        in the purpose statement of bucket_players(), but does not perform input validation and assumes
        that the `players` list is sorted by age asc.

        :param players: The sorted list of players to separate into buckets
        :return:        A set of sets where each set represents the players that will play in a game
        """
        buckets: Set[FrozenSet[PlayerID]] = set()
        idx = 0
        while idx < len(players):
            if len(players) - idx > 5:
                players_to_take = min(5, len(players) - idx - 3)
            elif len(players) - idx > 0:
                players_to_take = len(players)
            else:
                return buckets
            buckets.add(
                self._take_players(
                    players[idx : idx + players_to_take], players_to_take
                )
            )
            idx += players_to_take
        return buckets

    def _take_players(
        self, players: List[Tuple[PlayerID, PlayerAge]], num: int
    ) -> FrozenSet[PlayerID]:
        """
        Takes a list of players (identified by ID and age) and a number, returning a frozen set
        containing that number of player IDs from the front of the list.

        :param players: The list of players from which to generate the frozen set of IDs
        :param num: The number of player IDs to take from the front of the list
        :return: A frozen set containing the IDs of the first `num` players in `players`
        """
        return frozenset([pid for pid, _ in players[:num]])

    @validate_types
    def eliminate_players(
        self, live_players: Set[PlayerID], game_results: List[TournamentResult]
    ) -> Result[Set[PlayerID]]:
        """
        Given the set of live players and the list of game results returns the set of players which
        should be eliminated from the tournament.

        Players survive if they are in the first two sets of players in any of the given game results.

        :param live_players:    The set of live players represented by their player IDs
        :param game_results:    A set of game results for each of the games run by the administrator
        :return:                A set of the players that should be eliminated from the game
        """
        if flatten_leaderboards(game_results) != live_players:
            return error(
                "game results contain a different set of players than the set of live players"
            )
        survivors: Set[PlayerID] = set()
        for winners, _ in game_results:
            top_two_sets = [x for x in winners if x][:2]
            for item in top_two_sets:
                for pid in item:
                    survivors.add(pid)
        return ok(live_players - survivors)


@validate_types
def flatten_leaderboards(game_results: List[TournamentResult]) -> Set[PlayerID]:
    """
    Flatten the given list of leaderboards into a set of player IDs contained in all of the leaderboards

    :param game_results:    A list of tournament leaderboards
    :return:                A set of player IDs that are in the game results
    """
    ret = set()
    for game_result in game_results:
        for pid in flatten_leaderboard(game_result):
            ret.add(pid)
    return ret


@validate_types
def flatten_leaderboard(game_result: TournamentResult) -> Set[PlayerID]:
    """
    Flatten the given leaderboard into a set of player IDs contained in the given leaderboard

    :param game_result:     A tournament leaderboard
    :return:                A set of player IDs that are in the game result
    """
    ret: Set[PlayerID] = set()
    winners, cheaters = game_result
    for item in cheaters:
        ret.add(item)
    for items in winners:
        for player in items:
            ret.add(player)
    return ret
