"""
An interface for strategies as used by Player.player
"""
from typing import List, Tuple

from Common.board_position import BoardPosition
from Common.board_state import BoardState
from Common.color import ColorString
from Common.result import Result, error
from Common.rules import RuleChecker
from Common.tiles import PortID, Tile


class Strategy:
    # pylint: disable=no-self-use, unused-argument
    """
    Represents a Strategy as used by Player.player. A strategy is in charge of performing the intelligent portions
    of what a player does (eg calculating moves).
    """

    color: ColorString
    rule_checker: RuleChecker

    def __init__(self):
        self.rule_checker = RuleChecker()

    def set_color(self, color: ColorString) -> None:
        """
        Set the color this strategy is playing as.

        :param color: The ColorString that this strategy is playing as.
        """
        self.color = color

    def set_rule_checker(self, rule_checker: RuleChecker) -> None:
        """
        Set the rule checker that will be used by this game.

        :param rule_checker: The Rule Checker being used in this game.
        """
        self.rule_checker = rule_checker

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
        return error("Strategy does not implement method generate_first_move!")

    def generate_move(self, tiles: List[Tile], board_state: BoardState) -> Result[Tile]:
        """
        Generate a move by choosing from the given list of tiles and returning the move. `set_color`,
        `set_rule_checker`, and `generate_first_move` will be called prior to this method.

        :param tiles:           The set of tile options for the first move
        :param board_state:     The state of the current board
        :return:                A result containing the tile that will be placed for the given player
        """
        return error("Strategy does not implement method generate_move!")
