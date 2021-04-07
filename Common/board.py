"""
A module to represent a Tsuro board. A Tsuro board is a square grid of Tsuro tiles with colored tokens placed on
specific ports.

The Board class represents a mutable wrapper around immutable board states.
"""
import functools
from copy import deepcopy
from typing import Any, Callable, List, Optional, Set, Tuple, TypeVar, cast

from pyrsistent.typing import PMap

from Common.board_constraint import PhysicalConstraintChecker
from Common.board_observer import BoardObserver, LoggingObserver
from Common.board_position import BoardPosition
from Common.board_state import BoardState
from Common.color import ColorString
from Common.moves import InitialMove, IntermediateMove
from Common.result import Result, error, ok
from Common.tiles import Port, PortID, Tile
from Common.util import silenced_object
from Common.validation import validate_types

FuncResultT = TypeVar("FuncResultT", bound=Callable[..., Result[None]])


def atomic(func: FuncResultT) -> FuncResultT:
    """
    A decorator that can be used on methods on the Board class in order to ensure that they are atomic operations.
    Takes in a function that returns a Result and returns a function that returns a Result. If the returned result
    is an error, at run time resets self._board_state to the original version prior to the function invocation.

    Due to limitations of mypy's support for nested type variables, the wrapped function must return a Result[None]
    and it is not possible to return a Result[T].

    :param func:    The method on Board to wrap. The method must take in an argument `self` with type `Board` as
                    the first argument
    :return:        A wrapper version of the method that does not mutate the board state unless the entire operation
                    was successful
    """

    @functools.wraps(func)
    def inner(self: "Board", *args: Any, **kwargs: Any) -> Result[None]:
        copied_board_state = deepcopy(
            self._board_state  # pylint: disable=protected-access
        )
        ret: Result[None] = func(self, *args, **kwargs)
        if ret.is_error():
            self._board_state = copied_board_state  # pylint: disable=protected-access
        return ret

    return cast(FuncResultT, inner)


class Board:
    """
    Board is a mutable definition of the Board that is used by the referee. Board works via modifying
    the internal BoardState data to advance the game.
    """

    _board_state: BoardState

    def __init__(self, board_state: Optional[BoardState] = None):
        if board_state is None:
            board_state = BoardState()
        self._board_state = board_state
        self._observers: List[BoardObserver] = []

    @property
    def live_players(self) -> PMap[ColorString, Tuple[BoardPosition, PortID]]:
        """
        Get the data describing the live players in this board
        :return:    The live players represented as a map from a color to their position and port
        """
        return self._board_state.live_players

    @validate_types
    def add_observer(self, observer: BoardObserver) -> None:
        """
        Add the given board observer to this board. The board observer will then receive events
        detailing the key actions that happened on this board.

        :param observer:    The observer to add to this board
        :return:            None
        """
        self._observers.append(silenced_object(observer))

    @validate_types
    def remove_observer(self, observer: BoardObserver) -> None:
        """
        Remove the given
        :param observer:
        :return:
        """
        self._observers.remove(silenced_object(observer))

    @validate_types
    def get_board_state(self) -> BoardState:
        """
        Get a copy of the board state contained within this board

        :return:    The board state inside this Board
        """
        return deepcopy(self._board_state)

    @validate_types
    def validate_initial_move(self, move: InitialMove) -> Result[None]:
        """
        Validate the given initial move to ensure it adheres to a variety of physical constraints

        :param move:        The initial move to valid
        :return:            A result containing an error if the move is invalid or a result containing the value None
                            if there was no error
        """
        if move.player in self._board_state.live_players:
            return error(
                f"cannot place player {move.player} since the player is already on the board"
            )
        r_is_valid_initial_pos = PhysicalConstraintChecker.is_valid_initial_position(
            deepcopy(self._board_state), move.pos
        )
        if r_is_valid_initial_pos.is_error():
            return r_is_valid_initial_pos
        r_is_valid_initial_port = PhysicalConstraintChecker.is_valid_initial_port(
            deepcopy(self._board_state), move.pos, move.port
        )
        if r_is_valid_initial_port.is_error():
            return r_is_valid_initial_port
        return ok(None)

    @atomic
    @validate_types
    def initial_move(self, move: InitialMove) -> Result[None]:
        """
        Place the given initial move on this board

        :param move:        The initial move to place
        :return:            A result containing an error if the move is invalid or a result containing the value None
                            if there was no error and the move was placed successfully
        """
        validate_result = self.validate_initial_move(move)
        if validate_result.is_error():
            return validate_result
        return self.initial_move_with_scissors(move)

    @atomic
    @validate_types
    def initial_move_with_scissors(self, move: InitialMove) -> Result[None]:
        """
        Place an initial move without any validation (hence the with_scissors). This method is only
        recommended to be used with extreme care and not exposed to any untrusted users.

        :param move:    The initial move to place
        :return:        A result containing either none or an error message
        """
        self._board_state = self._board_state.with_change(
            added_tile_pos=(move.tile, move.pos),
            new_live_players=self._board_state.live_players.set(
                move.player, (move.pos, move.port)
            ),
        )
        return self._move_all_players_along_paths()

    @validate_types
    def validate_intermediate_move(self, move: IntermediateMove) -> Result[None]:
        """
        Validate the given intermediate move, ensuring that the player is still alive
        before making the move.

        :param move:        The intermediate move to validate
        :return:            A result containing an error if the move is invalid or a result containing the value None
                            if there was no error
        """
        if move.player not in self._board_state.live_players:
            return error(
                f"cannot place a tile for player {move.player} since they are not alive"
            )

        return ok(None)

    @atomic
    @validate_types
    def intermediate_move(self, move: IntermediateMove) -> Result[None]:
        """
        Place the given tile at the given position on this board.

        :param move:        The intermediate move to be placed
        :return:            A result containing an error if the move is invalid or a result containing the value None
                            if there was no error and the tile was placed successfully
        """
        validate_result = self.validate_intermediate_move(move)
        if validate_result.is_error():
            return validate_result

        pos_r = self._board_state.calculate_adjacent_position_of_player(move.player)

        if pos_r.is_error():
            return error(
                "cannot place tile for player %s: %s" % (move.player, pos_r.error())
            )
        pos = pos_r.value()

        if pos is None:
            return error(
                f"cannot place tile for player {move.player} since it would go off the edge of the board (this should "
                f"never happen!)"
            )

        if self._board_state.get_tile(pos) is not None:
            return error(
                f"cannot place for player {move.player} since it would be on top of an existing tile (this should"
                f"never happen!)"
            )

        # Assignment 6 states that if a move causes a loop it is legal (and the board must support it)
        # but that the expected behavior is to remove the players on the loop, not the place tile,
        # and accept the move.
        orig_board_state = deepcopy(self._board_state)
        temp_logging_observer = LoggingObserver()
        self.add_observer(temp_logging_observer)
        self._board_state = self._board_state.with_tile(move.tile, pos)
        r = self._move_all_players_along_paths()
        if r.is_error():
            return r
        if temp_logging_observer.entered_loop:
            # Placing this tile caused someone to enter a loop. So we undo any changes, delete the
            # people that were in the loop, and return ok
            self._board_state = orig_board_state
            for player in temp_logging_observer.entered_loop:
                self.remove_player(player)
        self.remove_observer(temp_logging_observer)
        return ok(None)

    @atomic
    @validate_types
    def place_tile_at_index_with_scissors(
        self, tile: Tile, pos: BoardPosition
    ) -> Result[None]:
        """
        Place a tile at the specified index. with_scissors because this does minimal validation of the
        tile placement and only verifies that it does not overwrite another tile.

        :param tile:
        :param pos:
        :return:
        """
        self._board_state = self._board_state.with_tile(tile, pos)
        return self._move_all_players_along_paths()

    @staticmethod
    @validate_types
    def create_board_from_initial_placements(
        initial_placements: List[InitialMove]
    ) -> Result["Board"]:
        """
        Create a board from the given list of initial placements. The list is ordered in the order that the moves will
        be applied.

        :param initial_placements:  A list of initial moves to be placed on the board. An initial move consists of
                                    a board position, a tile, a port ID, and a color string
        :return:                    A result containing either the board or an error
        """
        board = Board()
        for move in initial_placements:
            r = board.initial_move(move)
            if r.is_error():
                return error(
                    "failed to create board from set of initial placements: %s"
                    % r.error()
                )
        return ok(board)

    @staticmethod
    @validate_types
    def create_board_from_moves(
        initial_placements: List[InitialMove], moves: List[IntermediateMove]
    ) -> Result["Board"]:
        """
        Create a board from the given list of initial placements and the given list of subsequent moves. Both lists are
        ordered in the order that the moves will be applied.

        :param initial_placements:  A list of initial moves to be placed on the board. An initial move consists of
                                    a board position, a tile, a port ID, and a color string
        :param moves:               A result containing either the board or an error
        :return:                    A result containing either the board or an error
        """
        board_r = Board.create_board_from_initial_placements(initial_placements)
        if board_r.is_error():
            return board_r
        board = board_r.value()
        for move in moves:
            r = board.intermediate_move(move)  # pylint: disable=no-member
            if r.is_error():
                return error(f"failed to create board from moves: {r.error()}")
        return ok(board)

    def remove_player(self, player: ColorString) -> None:
        """
        Remove the given player from this Board

        :param player:  The color of the player to remove from the board
        """
        self._board_state = self._board_state.with_live_players(
            self._board_state.live_players.remove(player)
        )

    @validate_types
    def _move_all_players_along_paths(self) -> Result[None]:
        """
        Move all players along their paths until they hit the end of a path or the edge of a board. If
        they hit the end of the board, remove them from the BoardState.

        :return:                A Result containing either an error or None
        """
        to_remove = []
        for player in self._board_state.live_players:
            r = self._move_player_along_path(player)
            if r.is_error():
                return error(r.error())
            if r.value():
                to_remove.append(player)

        for player in to_remove:
            self.remove_player(player)
            for observer in self._observers:
                observer.player_exited_board(player)

        return ok(None)

    @validate_types
    def _move_player_along_path(self, player: ColorString) -> Result[bool]:
        """
        Move the given player along their path until they hit the end of a path or the edge of a board. Returns a
        result containing a boolean that indicates whether or not the player hit the edge of the board.

        If the player's path forms an infinite loop, removes the player from the board.

        :param player:  The color of the player
        :return:        An result containing whether the player hit the edge of the board or an error
        """
        seen_pos_port: Set[Tuple[BoardPosition, PortID]] = set()

        while True:
            r = self._board_state.get_position_of_player(player)
            if r.is_error():
                return error(
                    "failed to move player %s along path: %s" % (player, r.error())
                )
            pos, port = r.value()

            if (pos, port) in seen_pos_port:
                for observer in self._observers:
                    observer.player_entered_loop(player)
                # They entered an infinite loop and must be removed
                return ok(True)
            seen_pos_port.add((pos, port))

            r2 = self._board_state.calculate_adjacent_position_of_player(player)
            if r2.is_error():
                return error(
                    "failed to move player %s along path: %s" % (player, r.error())
                )
            next_pos = r2.value()
            if next_pos is None:
                # They hit the edge of the board so remove them from the list of live players
                return ok(True)

            next_tile = self._board_state.get_tile(next_pos)

            if next_tile is None:
                # They didn't hit the edge of the board so they don't need to be removed
                return ok(False)

            next_port = Port.get_adjoining_port(port)

            next_next_port = next_tile.get_port_connected_to(next_port)

            self._board_state = self._board_state.with_live_players(
                self._board_state.live_players.set(player, (next_pos, next_next_port))
            )
