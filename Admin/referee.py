"""
Holds a Tsuro referee capable of running a single game of Tsuro.
"""
from copy import deepcopy
from typing import Dict, Iterator, List, Optional, Set

from Common.board import Board
from Common.color import AllColors, ColorString
from Common.moves import InitialMove, IntermediateMove
from Common.player_interface import PlayerInterface
from Common.result import Result, error, ok
from Common.rules import RuleChecker
from Common.tiles import Tile, load_tiles_from_json
from Common.tsuro_types import GameResult
from Common.util import silenced_object, timeout
from Common.validation import validate_types
from Admin.game_observer import RefereeObserver

TIMEOUT = 3

def deterministic_tile_iterator() -> Iterator[Tile]:
    """
    A simple deterministic infinite tile iterator that yields tiles in order by their
    TileIndex.

    :return:    An iterator of tiles
    """
    while True:
        for _, tile in load_tiles_from_json():
            yield tile


class Referee:
    """
    Represents the referee for a game of Tsuro. Runs a full game with the specified players. A instance of the
    Referee class can only be used for a single game and cannot be reused.

    In the event of abnormal conditions, the referee will handle them in the following ways:
    - Player cheats           -> Player is eliminated from the game
    - Player raises exception -> Player is eliminated from the game
    - Player returns an error -> Player is eliminated from the game
    - Player takes too long   -> Not currently handled
    """

    _players: Dict[ColorString, PlayerInterface]
    _rule_checker: Optional[RuleChecker]
    _tile_iterator: Optional[Iterator[Tile]]
    _cheaters: Set[ColorString]
    _leaderboard: List[Set[ColorString]]
    _observers: List[RefereeObserver]

    def __init__(self) -> None:
        """
        Create a new Referee.
        """
        self._players = {}
        self._rule_checker = None
        self._tile_iterator = None
        self._leaderboard = []
        self._cheaters: Set[ColorString] = set()
        self._observers = []

    @validate_types
    def add_observer(self, observer: RefereeObserver):
        self._observers.append(observer)

    @validate_types
    def set_players(self, players: List[PlayerInterface]) -> Result[List[ColorString]]:
        """
        Add the given players (ordered by age, decreasing) to the game. Ties for age can be represented in either order.
        Returns an error if `len(players)` is greater than 5 or less than 3, or if the method has already been called.

        :param players: Players for this referee to use in a game. Allows only 3-5 players.
        :return:        The list of colors that will be assigned to those players.
        """
        if self._players:
            return error("players have already been set for this game.")
        if len(players) < 3 or len(players) > 5:
            return error(f"there must be between 3 and 5 players, not {len(players)}.")
        if len(set(players)) != len(players):
            return error(
                f"the given set of players contains duplicates (or players that do not "
                f"implement __hash__, __eq__)"
            )

        assigned_colors = AllColors[: len(players)]
       
        self._players = {
            color: silenced_object(player)
            for color, player in zip(assigned_colors, players)
        }
       
        for observer in self._observers:
            observer.players_added(assigned_colors)
        return ok(assigned_colors)

    @validate_types
    def set_rule_checker(self, rule_checker: RuleChecker) -> None:
        """
        Set the rule checker to be used by this referee. Must be called prior to calling run_game().

        :param rule_checker: The rule checker that the referee should use.
        """
        self._rule_checker = rule_checker

    @validate_types
    def set_tile_iterator(self, tile_iterator: Iterator[Tile]) -> None:
        """
        Set the iterator of tiles to be used by this referee. Must be infinite and only be used by this referee.

        :param tile_iterator: The infinite tile iterator to be used by this referee.
        """
        self._tile_iterator = tile_iterator

    def run_game(self) -> Result[GameResult]:
        """
        Run an entire game of Tsuro with the players that have been added to this referee. Returns the result
        of the game.

        A list of players, a rule checker, and a tile iterator must have already been set on this referee
        prior to calling run_game.

        :return: The GameResult at the end of the game, or an error if something goes wrong.
        """
        if not self._players:
            return error("must add players to this referee")
        if not self._rule_checker:
            return error("must add a rule checker to this referee")
        if not self._tile_iterator:
            return error("must add a tile iterator to this referee")

        self._initialize_players()
        board = Board()

        # Run the initial turns
        r = self._run_game_initial_turns(board)
        if r.is_error():
            return error(r.error())

        # Run the intermediate turns
        while True:
            if len(board.live_players) <= 1:
                break

            r = self._run_game_single_round(board)
            if r.is_error():
                return error(r.error())

        return self._generate_game_result(board)

    def _initialize_players(self) -> None:
        """
        Initialize the players contained within this referee according to the player interface
        """
        assert self._rule_checker
        for color, player in self._players.items():
            self._handle_player_timeout(color, lambda: player.set_color(color))
            self._handle_player_timeout(color, lambda: player.set_players(list(set(self._players.keys()) - {color})))

    def _generate_game_result(self, board: Board) -> Result[GameResult]:
        """
        Generate a GameResult once a game of Tsuro is complete based off of the data in self.cheaters,
        self.players_eliminated_in_round, and board. Must only be called once the game is over and 0 or 1
        players remain on the board.

        :param board:   The board at the end of the game
        :return:        The game result which contains a leaderboard and a list of cheaters
        """
        # Add the last man standing to the list of eliminated players
        self._leaderboard.append(set(board.live_players.keys()))
        leaderboard = [x for x in reversed(self._leaderboard) if x]

        # Return the leaderboard and the cheaters and notify observers
        results = deepcopy((leaderboard, self._cheaters))
        for observer in self._observers:
            observer.game_result(results)
        return ok(results)

    def _remove_cheaters(self, board: Board) -> None:
        """
        Remove anyone in self.cheaters from the list of players and from the list of currently live players

        :param board:   The board to remove players from
        """
        for player in self._cheaters:
            if player in self._players:
                del self._players[player]
            if player in board.live_players:
                board.remove_player(player)
                for observer in self._observers:
                    observer.cheater_removed(player, board.get_board_state())

    def _get_tiles(self, num_tiles: int) -> List[Tile]:
        """
        Get N tiles from the internal tile iterator
        :param num_tiles:   The number of tiles
        :return:            A list of retrieved tiles
        """
        if self._tile_iterator is None:
            raise ValueError(
                "Cannot call _get_tiles(n) prior to setting the tile iterator!"
            )

        return [next(self._tile_iterator) for _ in range(num_tiles)]
    
    def _confirm_all_components(self) -> Result[None]:
        """
        Checks that all components required for the referee to run (players, rules, tile iterator) exist
        """
        if not self._players:
            return error("must add players to this referee")
        if not self._rule_checker:
            return error("must add a rule checker to this referee")
        if not self._tile_iterator:
            return error("must add a tile iterator to this referee")
        return ok(None)

    def _run_game_initial_turns(self, board: Board) -> Result[None]:
        """
        Run the first step of a Tsuro game: prompting every player for their initial move. Apply the
        changes to this board to the fields contained within this referee.

        :param board:   The board to run the game on
        :return:        A result containing either None or an error
        """
        r_components = self._confirm_all_components()
        if r_components.is_error(): return r_components

        for color, player in self._players.items():
            tiles = self._get_tiles(3)
            for observer in self._observers:
                observer.initial_move_offered(color, tiles, board.get_board_state())

            r_initial_move = self._get_check_initial_move(board, color, player, tiles)
            if r_initial_move.is_error(): continue
            
            r = board.initial_move(r_initial_move.value())
            if r.is_error():
                return error(r.error())

        self._remove_cheaters(board)
        return ok(None)

    def _get_check_initial_move(
        self, board: Board, color: ColorString, player: PlayerInterface, tiles: List[Tile]
        ) -> Result[InitialMove]:
        """
        Gets the initial move from the player and checks whether it is valid based on the rulechecker. If any errors, the player is added as a cheater.
        Returns an error if cheating, or the chosen move if it is valid
        """
        r_initial_move = self._handle_player_timeout(color, lambda: player.generate_first_move(deepcopy(tiles), board.get_board_state()))
        if r_initial_move.is_error():
            self._cheaters.add(color)
            return error(r_initial_move.error())

        pos, tile, port = r_initial_move.value()
        initial_move = InitialMove(pos, tile, port, color)

        for observer in self._observers:
            observer.initial_move_played(color, tiles, board.get_board_state(), initial_move)

        r_rule = self._rule_checker.validate_initial_move(board.get_board_state(), tiles, initial_move)
        if r_rule.is_error():
            self._cheaters.add(color)
            return error(r_initial_move.error())

        return ok(initial_move)

    def _run_game_single_round(self, board: Board) -> Result[None]:
        """
        Run the second step of a Tsuro game: prompting every player for an intermediate move. Apply the
        changes to this board to the fields contained within this referee.

        :param board:           The board to run the game on
        :return:                A result containing either None or an error
        """
        r_components = self._confirm_all_components()
        if r_components.is_error(): return r_components

        alive_at_start_of_round = set(board.live_players.keys())
        for color, player in list(self._players.items()):
            if color not in board.live_players.keys():
                # They were killed by someone else so continue
                continue

            tiles = self._get_tiles(2)
            for observer in self._observers:
                observer.intermediate_move_offered(color, tiles, board.get_board_state())

            r_intermediate_move = self._get_check_intermediate_move(color, board, tiles, player)
            if r_intermediate_move.is_error(): continue

            r = board.intermediate_move(r_intermediate_move.value())
            if r.is_error():
                return error(r.error())

        alive_at_end_of_round = set(board.live_players.keys())
        self._leaderboard.append(set())
        self._handle_players_lost_in_round(board, alive_at_start_of_round, alive_at_end_of_round)
        
        return ok(None)

    def _handle_players_lost_in_round(
        self, board: Board, alive_at_start_of_round: Set, alive_at_end_of_round: Set
        ):
        """
        Removes all players who died during a round from the game and adds them to the leaderboard.
        """
        for killed_player in (alive_at_start_of_round - alive_at_end_of_round - self._cheaters):
            self._leaderboard[-1].add(killed_player)
            del self._players[killed_player]
            
            for observer in self._observers:
                observer.player_eliminated(killed_player, board.get_board_state())

        self._remove_cheaters(board)

    def _get_check_intermediate_move(
        self, color:ColorString, board: Board, tiles: List[Tile], player: PlayerInterface
        ) -> Result[IntermediateMove]:
        """
        Gets the intermediate move from the player and checks whether it is valid based on the rulechecker. If any errors, the player is added as a cheater.
        Returns an error if cheating, or the chosen move if it is valid
        """
        r_move = self._handle_player_timeout(color, lambda: player.generate_move(deepcopy(tiles), board.get_board_state()))
        if r_move.is_error():
            self._cheaters.add(color)
            return error(r_move.error())

        intermediate_move = IntermediateMove(r_move.value(), color)
        r_rule = self._rule_checker.validate_move(board.get_board_state(), tiles, intermediate_move)

        for observer in self._observers:
            observer.intermediate_move_played(color, tiles, board.get_board_state(), intermediate_move, r_rule.is_ok())

        if r_rule.is_error():
            self._cheaters.add(color)
            return error(r_rule.error())

        return ok(intermediate_move)

    def _handle_player_timeout(self, color, func):
        """
        Calls the method on a player with a timeout. Returns the same value
        as the given function if the function takes less than three seconds
        to run. Otherwise, the player took too long to play, and is added
        to the list of cheaters.
        """
        try:
            with timeout(TIMEOUT):
                return func()
        except:
            self._cheaters.add(color)
