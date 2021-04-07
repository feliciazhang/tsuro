"""
An interface and implementation for a Tsuro rule checker. See Planning/rules.md
"""

from copy import deepcopy
from typing import List

from Common.board import Board
from Common.board_observer import LoggingObserver
from Common.board_state import BoardState
from Common.moves import InitialMove, IntermediateMove
from Common.result import Result, error, ok
from Common.tiles import Tile
from Common.validation import validate_types

EXPECTED_TILE_COUNT_INITIAL_MOVE = 3
EXPECTED_TILE_COUNT_INTERMEDIATE_MOVE = 2
LOOP_ERROR = "loopy move when this does not create a loop"
SUICIDE_ERROR = "suicidal move when this does not cause a suicide"

class RuleChecker:
    # pylint: disable=no-self-use
    """
    An example class adhering to the rule checker interface. This implements the rules defined
    in assignment 4: http://www.ccs.neu.edu/home/matthias/4500-f19/4.html
    """

    @validate_types
    def validate_initial_move(  # pylint: disable=too-many-arguments
        self, board_state: BoardState, tile_choices: List[Tile], move: InitialMove
    ) -> Result[None]:
        """
        Validate the given initial move when the player was given the choice of tile_choices.

        :param board_state:     The board state the move is being applied to
        :param tile_choices:    The list of tiles the player was allowed to choose from
        :param move:            The initial move to validate
        :return:                A result containing either None (if the move is valid) or an error
                                if the move is invalid. If the move is invalid, the error contains
                                a description of why it is invalid.
        """
        conditions_r = self.check_valid_move_params(tile_choices, move.tile, EXPECTED_TILE_COUNT_INITIAL_MOVE)
        if conditions_r.is_error(): return conditions_r

        board = Board(deepcopy(board_state))
        return board.validate_initial_move(move)

    @validate_types
    def validate_move(
        self, board_state: BoardState, tile_choices: List[Tile], move: IntermediateMove
    ) -> Result[None]:
        """
        Validate the given intermediate move when the player was given the choice of tile_choices.

        :param board_state:     The board state the move is being applied to
        :param tile_choices:    The list of tiles the player was allowed to choose from
        :param move:            The intermediate move to validate
        :return:                A result containing either None (if the move is valid) or an error
                                if the move is invalid. If the move is invalid, the error contains
                                a description of why it is invalid.
        """
        conditions_r = self.check_valid_move_params(tile_choices, move.tile, EXPECTED_TILE_COUNT_INTERMEDIATE_MOVE)
        if conditions_r.is_error(): return conditions_r

        board = Board(deepcopy(board_state))
        r = board.validate_intermediate_move(move)
        if r.is_error():
            return r

        loop_r = self.is_legal_for_condition(self.move_creates_loop, board_state, tile_choices, move, LOOP_ERROR)
        if loop_r.is_error(): return loop_r
        
        suicide_r = self.is_legal_for_condition(self.is_move_suicidal, board_state, tile_choices, move, SUICIDE_ERROR)
        if suicide_r.is_error(): return suicide_r

        return ok(None)

    @validate_types
    def check_valid_move_params(self, tile_choices: List[Tile], tile: Tile, expected: int) -> Result[None]:
        """
        Checks whether the tile that the player has chosen is one of the given tiles and that
        the number of tiles given is the expected number for the type of turn.
        If either condition is invalid, an error is returned

        :param tile_choices:    The list of tiles the player was allowed to choose from
        :param tile:            The chosen tile to validate
        """
        if len(tile_choices) != expected:
            return error(
                f"cannot validate move with {len(tile_choices)} tile choices "
                f"(expected {expected})"
            )
        if tile not in tile_choices:
            return error(
                f"tile {tile} is not in the list of tiles {tile_choices} the player was given"
            )
        return ok(None)

    @validate_types
    def is_move_illegal(
        self, board_state: BoardState, move: IntermediateMove
    ) -> Result[bool]:
        """
        Returns whether the given move is illegal without checking anything that relies on the list of
        tile options. Note that this may return True for a move that is actually legal since it is
        the player's only option.

        :param board_state:     The board state to apply the move to
        :param move:            The intermediate move being applied
        :return:                A Result containing whether or not the move is illegal
        """
        # Suicide is illegal
        suicide_r = self.is_move_suicidal(board_state, move)
        if suicide_r.is_error():
            return suicide_r
        if suicide_r.value():
            return ok(True)

        # It is also illegal to put anyone into a loop
        loop_r = self.move_creates_loop(board_state, move)
        return loop_r

    @validate_types
    def is_legal_for_condition(
        self, legality_check, board_state, tile_choices: List[Tile], move: IntermediateMove, error_message
    ) -> Result[None]:
        """
        Checks whether a move is legal against a certain legality check (ie loop or suicide) in that 
        the move is only legal if it passes that check, or if all options fail that check.

        :param board_state:     The board state to apply the move to
        :param move:            The intermediate move being applied
        :param legality_check:  The function that checks the validity of the move against a certain rule
        :param tile_choices:    The tile options provided
        """
        legal_r = legality_check(board_state, move)
        if legal_r.is_error():
            return error(legal_r.error())
        if legal_r.value():
            for tile_choice in tile_choices:
                for rotated_tile_choice in tile_choice.all_rotations():
                    legal_r = legality_check(
                        board_state, IntermediateMove(rotated_tile_choice, move.player)
                    )
                    if legal_r.is_error():
                        return error(legal_r.error())
                    if not legal_r.value():
                        return error(
                            f"player chose a {error_message}: {rotated_tile_choice}"
                        )
        return ok(None)

    @validate_types
    def move_creates_loop(
        self, board_state: BoardState, move: IntermediateMove
    ) -> Result[bool]:
        """
        Returns whether or not the given move creates a loop for anyone on the board. Note that this returns False if a
        loop is created that no player is on.

        :param board_state:     The board state to apply the move to
        :param move:            The intermediate move being applied
        :return:                A Result containing whether or not the move creates a loop for anyone on the baord
        """
        logging_observer = LoggingObserver()
        board = Board(deepcopy(board_state))
        board.add_observer(logging_observer)
        r = board.intermediate_move(move)
        if r.is_error():
            return error(r.error())
        return ok(len(logging_observer.entered_loop) > 0)

    @validate_types
    def is_move_suicidal(
        self, board_state: BoardState, move: IntermediateMove
    ) -> Result[bool]:
        """
        Returns whether the given intermediate move is suicidal. A suicidal move is a move that
        results in the player who placed the move leaving the board but NOT if a loop is caused.

        :param board_state:     The board state the move is being applied to
        :param move:            The intermediate move to check for suicideness
        :return:                A result containing a boolean or an error. If it contains a value
                                the boolean specifies whether or not the move is suicidal.
        """
        logging_observer = LoggingObserver()
        if move.player not in board_state.live_players:
            return error(
                f"player {move.player} is not alive thus the move cannot be suicidal"
            )
        board = Board(deepcopy(board_state))
        board.add_observer(logging_observer)
        r = board.intermediate_move(move)
        if r.is_error():
            return error(r.error())
        return ok(move.player not in board.live_players and len(logging_observer.entered_loop) <= 0)
