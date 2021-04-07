"""
A module to represent a Tsuro player, handling all communication between referees, strategies, and observers.
"""
from typing import List, Tuple

from Common.board_position import BoardPosition
from Common.board_state import BoardState
from Common.color import ColorString
from Common.moves import InitialMove, IntermediateMove
from Common.player_interface import PlayerInterface
from Common.result import Result
from Common.rules import RuleChecker
from Common.tiles import PortID, Tile
from Common.tsuro_types import GameResult
from Common.util import silenced_object
from Player.observer_interface import PlayerObserver
from Player.strategy import Strategy


class Player(PlayerInterface):
    """
    Designed to perform all mechanical tasks of the player by handling communication between referees,
    strategies, and observers. Doesn't perform validation of the moves given by the strategy, but does
    silence all errors from observers.
    """

    strategy: Strategy
    color: ColorString

    def __init__(self, strategy: Strategy) -> None:
        self.strategy = strategy
        self.observers: List[PlayerObserver] = []

    def set_color(self, color: ColorString) -> None:
        """
        Set the color of this Player.

        :param color: The ColorString assigned to this player.
        """
        for observer in self.observers:
            observer.set_color(color)

        self.color = color
        self.strategy.set_color(color)

    def set_players(self, players: List[ColorString]) -> None:
        """
        Set the list of other players playing in the Tsuro game

        :param players:     The list of players represented as a list of colors
        """
        for observer in self.observers:
            observer.set_players(players)

    def set_rule_checker(self, rule_checker: RuleChecker) -> None:
        """
        Set the rule checker that will be used by this game.

        :param rule_checker: The Rule Checker being used in this game.
        """
        self.strategy.set_rule_checker(rule_checker)

    def generate_first_move(
        self, tiles: List[Tile], board_state: BoardState
    ) -> Result[Tuple[BoardPosition, Tile, PortID]]:
        """
        Generate the first move by choosing from the given list of tiles. Returns the move along with
        the port that the player's token should be placed on. `set_color` and `set_rule_checker` will
        be called prior to this method.

        :param tiles:           The set of tile options for the first move
        :param board_state:     The state of the current board
        :return:                A result containing a tuple containing the board position, tile, and port ID
                                for the player's initial move
        """
        for observer in self.observers:
            observer.initial_move_offered(tiles, board_state)

        r_move = self.strategy.generate_first_move(tiles, board_state)
        if r_move.is_error():
            return r_move
        board_position, tile, port = r_move.value()

        for observer in self.observers:
            observer.initial_move_played(
                tiles, board_state, InitialMove(board_position, tile, port, self.color)
            )
        return r_move

    def generate_move(self, tiles: List[Tile], board_state: BoardState) -> Result[Tile]:
        """
        Generate a move by choosing from the given list of tiles and returning the move. `set_color`,
        `set_rule_checker`, and `generate_first_move` will be called prior to this method.

        :param tiles:           The set of tile options for the first move
        :param board_state:     The state of the current board
        :return:                A result containing the tile that will be placed for the given player
        """
        for observer in self.observers:
            observer.intermediate_move_offered(tiles, board_state)

        r_move = self.strategy.generate_move(tiles, board_state)
        if r_move.is_error():
            return r_move

        for observer in self.observers:
            observer.intermediate_move_played(
                tiles, board_state, IntermediateMove(r_move.value(), self.color)
            )
        return r_move

    def game_result(self, results: GameResult) -> None:
        """
        Called at the end of a game to provide the results of the game. See the definition of
        GameResult for a description of this data type. Only passes results to observers.

        :param results:     The results of the completed game
        """
        for observer in self.observers:
            observer.game_result(results)

    def add_observer(self, observer: PlayerObserver) -> None:
        """
        Add the given player observer to this player. The player must support adding multiple player
        observers and sending events to all of the adding observers. See the definition of the
        PlayerObserver interface for information on the observer methods.

        :param observer:    A player observer to add to this interface that will receive all events
        """
        self.observers.append(silenced_object(observer))
