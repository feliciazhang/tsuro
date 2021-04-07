"""
Represents an interface for Players
"""
from typing import List, Tuple

from Common.board_position import BoardPosition
from Common.board_state import BoardState
from Common.color import ColorString
from Common.result import Result
from Common.rules import RuleChecker
from Common.tiles import PortID, Tile
from Common.tsuro_types import GameResult
from Player.observer_interface import PlayerObserver


class PlayerInterface:
    """
    Represents an automated Tsuro player that plays in a single game of Tsuro.
    """

    def set_color(self, color: ColorString) -> None:
        """
        Set the color of this Player.

        :param color: The ColorString assigned to this player.
        """

    def set_players(self, players: List[ColorString]) -> None:
        """
        Set the complete list of players playing in the Tsuro game. Includes the color of this player.

        :param players:     The list of players represented as a list of colors
        """

    def set_rule_checker(self, rule_checker: RuleChecker) -> None:
        """
        Set the rule checker that will be used by this game.

        :param rule_checker: The Rule Checker being used in this game.
        """

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

    def generate_move(self, tiles: List[Tile], board_state: BoardState) -> Result[Tile]:
        """
        Generate a move by choosing from the given list of tiles and returning the move. `set_color`,
        `set_rule_checker`, and `generate_first_move` will be called prior to this method.

        :param tiles:           The set of tile options for the first move
        :param board_state:     The state of the current board
        :return:                A result containing the tile that will be placed for the given player
        """

    def game_result(self, results: GameResult) -> None:
        """
        Called at the end of a game to provide the results of the game. See the definition of
        GameResult for a description of this data type.

        :param results:     The results of the completed game
        """

    def add_observer(self, observer: PlayerObserver) -> None:
        """
        Add the given player observer to this player. The player must support adding multiple player
        observers and sending events to all of the adding observers. See the definition of the
        PlayerObserver interface for information on the observer methods. Note that the observer must
        be given the observed player's color and the colors of everyone else that is playing.

        :param observer:    A player observer to add to this interface that will receive all events
        """

    def notify_won_tournament(self) -> None:
        """
        Notify the player that they won a tournament that they participated in
        """
