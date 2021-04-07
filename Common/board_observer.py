"""
Holds the interface for Board observers that observe events emitted by a Tsuro board. While this observer was not
specifically required by any of the assignments, it is an easy way for things to observe what happened when a move
was played against a board. Used by the rule checker in order to determine what happened when simulating a move.
"""

from typing import List

from Common.color import ColorString
from Common.validation import validate_types


class BoardObserver:
    # pylint: disable=no-self-use, unused-argument
    """
    The main interface for Board Observers with no action taken
    """

    def player_exited_board(self, player: ColorString) -> None:
        """
        An event handler for when a player exited a Tsuro board.

        :param player:  The player that exited the board
        """

    def player_entered_loop(self, player: ColorString) -> None:
        """
        An event handler for when a player entered an infinite loop on a Tsuro board.

        :param player:  The player that entered the infinite loop on the board
        """


class LoggingObserver(BoardObserver):
    """
    A Board Observer that logs all events to arrays containing the events. Useful for logging purposes
    or if one wishes to simply log events and respond to them asynchronously.
    """

    def __init__(self) -> None:
        self.entered_loop: List[ColorString] = []
        self.exited_board: List[ColorString] = []

    @validate_types
    def player_entered_loop(self, player: ColorString) -> None:
        """
        An event handler for when a player entered an infinite loop on a Tsuro board. Logs the player that exited to
        self.entered_loop.

        :param player:  The player that entered the infinite loop on the board
        """
        self.entered_loop.append(player)

    @validate_types
    def player_exited_board(self, player: ColorString) -> None:
        """
        An event handler for when a player exited a Tsuro board. Logs the player that exited to self.exited_board.

        :param player:  The player that exited the board
        """
        self.exited_board.append(player)

    @validate_types
    def all_messages(self) -> List[str]:
        """
        Get all of the messages logged to this observer
        :return:    A list of strings representing the logged messages
        """
        return [f"entered_loop: {item}" for item in self.entered_loop] + [
            f"exited_board: {item}" for item in self.exited_board
        ]
