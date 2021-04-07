"""
Implementation for the board integration test harness as described in assignment 4:
http://www.ccs.neu.edu/home/matthias/4500-f19/4.html
"""

import json
from typing import Set, Tuple

from Common.action import ActionPat, InitialPlace, IntermediatePlace, TilePat
from Common.board import Board
from Common.board_observer import LoggingObserver
from Common.board_position import BoardPosition
from Common.json_stream import StdinStdoutJSONStream
from Common.moves import InitialMove, IntermediateMove
from Common.tiles import (
    PortID,
    network_port_id_to_port_id,
    port_id_to_network_port_id,
    tile_pattern_to_tile,
    tile_to_index,
    tile_to_rotation_angle,
)
from Common.tsuro_types import JSON

# If DEBUG, then open the board in google-chrome for debugging purposes
DEBUG = False


def setup_board(board_setup_data: JSON) -> Board:
    """
    Setup the board according to the given board setup data. This is the first JSON value read
    from the integration test which is an array of initial-place or intermediate-place. Raises an
    exception if the input is invalid in any way.

    :param board_setup_data:    An array containg either initial-place elements or intermediate-place
                                elements
    :return:                    A board created from the setup data
    """
    board = Board()
    for item in board_setup_data:
        if len(item) == 5:
            initial_place = InitialPlace.from_json(item)
            r = board.initial_move_with_scissors(
                InitialMove(
                    BoardPosition(initial_place.x_index, initial_place.y_index),
                    tile_pattern_to_tile(
                        initial_place.tile_pat.tile_index,
                        initial_place.tile_pat.rotation_angle,
                    ),
                    network_port_id_to_port_id(initial_place.port),
                    initial_place.player,
                )
            )
            if r.is_error():
                raise Exception(r.error())
        elif len(item) == 3:
            intermediate_place = IntermediatePlace.from_json(item)
            r = board.place_tile_at_index_with_scissors(
                tile_pattern_to_tile(
                    intermediate_place.tile_pat.tile_index,
                    intermediate_place.tile_pat.rotation_angle,
                ),
                BoardPosition(intermediate_place.x_index, intermediate_place.y_index),
            )
            if r.is_error():
                raise Exception(r.error())
        else:
            raise Exception(f"Failed to parse JSON input: {item}")
    return board


def try_display_board(board: Board) -> None:
    """

    :param board:
    :return:
    """
    try:
        if DEBUG:
            board.get_board_state().debug_display_board()
    except Exception:  # pylint: disable=broad-except
        pass


def print_and_exit(msg: JSON, board: Board) -> None:
    """
    Print the given JSON value to stdout and if DEBUG then attempt to display the board via google-chrome
    :param msg:     The message to print to stdout
    :param board:   The board to maybe display to the user
    :return:        None
    """
    try_display_board(board)
    print(json.dumps(msg))
    exit(0)


def main() -> None:
    """
    Main function for the xboard integration test. Creates a board, applies action pats, and prints
    data to stdout as described in assignment 4: http://www.ccs.neu.edu/home/matthias/4500-f19/4.html
    :return:    None
    """
    stdin_stream = StdinStdoutJSONStream()
    board = setup_board(stdin_stream.receive_message().assert_value())

    logging_observer = LoggingObserver()
    board.add_observer(logging_observer)

    if "red" not in board.live_players:
        print_and_exit("red never played", board)

    for act_pat_json in stdin_stream.message_iterator():
        act_pat = ActionPat.from_json(act_pat_json.assert_value())
        r = board.intermediate_move(
            IntermediateMove(
                tile_pattern_to_tile(
                    act_pat.tile_pat.tile_index, act_pat.tile_pat.rotation_angle
                ),
                act_pat.player,
            )
        )
        if r.is_error():
            raise Exception(r.error())
        if logging_observer.entered_loop:
            print_and_exit("infinite", board)

        seen_pos_port: Set[Tuple[BoardPosition, PortID]] = set()
        for (pos, port) in board.live_players.values():
            if (pos, port) in seen_pos_port:
                print_and_exit("collision", board)
            seen_pos_port.add((pos, port))

        if "red" not in board.live_players:
            print_and_exit("red died", board)

    red_pos, red_port = board.live_players["red"]
    til = board.get_board_state().get_tile(red_pos)
    if til is None:
        raise Exception("There is no tile at red's position - this should never happen")
    tile_pat = TilePat(tile_to_index(til), tile_to_rotation_angle(til))
    print_and_exit(
        [
            tile_pat.to_json(),
            "red",
            port_id_to_network_port_id(red_port),
            red_pos.x,
            red_pos.y,
        ],
        board,
    )


if __name__ == "__main__":
    main()
