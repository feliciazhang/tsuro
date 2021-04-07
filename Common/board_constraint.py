"""
A module that includes a static class that can be used to check moves for violating physical constraints.
"""
from typing import TYPE_CHECKING

from Common import result
from Common.board_position import BoardPosition
from Common.result import ok
from Common.tiles import PortID
from Common.validation import validate_types

if TYPE_CHECKING:
    # Prevent an import loop by only importing if we are type checking
    from Common.board_state import BoardState  # isort:skip


class PhysicalConstraintChecker:
    """
    A static class used for checking that certain moves don't violate physical constraints when applied
    to a board. Abstracted out of the Board class so that strategies can also easily check physical constraints
    and to increase testability.
    """

    @staticmethod
    @validate_types
    def is_valid_initial_position(
        board_state: "BoardState", pos: BoardPosition
    ) -> result.Result[None]:
        """
        Returns whether the given position is a valid position to place a tile on for an initial move.

        :param board_state:     The current state of the board
        :param pos:             The board position to check
        :return:                A result containing an error if it is invalid otherwise a result containing None
        """
        if board_state.get_tile(pos) is not None:
            return result.error(
                f"cannot place tile at position {pos} since there is already a tile at that position"
            )
        if not pos.is_edge():
            return result.error(
                f"cannot make an initial move at position {pos} since it is not on the edge"
            )
        if not board_state.surrounding_positions_are_empty(pos):
            return result.error(
                f"cannot make an initial move at position {pos} since the surrounding tiles are not all empty"
            )
        return ok(None)

    @staticmethod
    @validate_types
    def is_valid_initial_port(
        board_state: "BoardState", pos: BoardPosition, port: PortID
    ) -> result.Result[None]:
        """
        Returns whether the given port is a valid port for a player to be on if a tile were to be placed at the given
        position.

        :param board_state:     The current state of the board
        :param pos:             The board position to check
        :param port:            The port to check
        :return:                A result containing an error if it is invalid otherwise a result containing None
        """
        r = PhysicalConstraintChecker.is_valid_initial_position(board_state, pos)
        if r.is_error():
            return r
        if not board_state.port_faces_interior(pos, port):
            return result.error(
                f"cannot make an initial move at position {pos}, port {port} since it does not "
                f"face the interior of the board"
            )
        return ok(None)
