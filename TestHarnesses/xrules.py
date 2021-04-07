"""
An implementation for the experimentation task in Assignment 6. Receives board state from stdin and a
move. Validates the move using the rule checker and outputs "legal" or "cheating"
"""
from typing import List

from Common.action import ActionPat
from Common.json_stream import StdinStdoutJSONStream
from Common.moves import IntermediateMove
from Common.rules import RuleChecker
from Common.tiles import Tile, index_to_tile, tile_pattern_to_tile
from TestHarnesses.xboard import setup_board

# If DEBUG, then open the board in google-chrome for debugging purposes
DEBUG = False


def main() -> None:
    """
    Connect to the server at host:port via TCP to render a board state to the GUI via a GraphicalPlayerObserver
    """
    json_stream = StdinStdoutJSONStream()

    state_pats_json_r = json_stream.receive_message()
    board = setup_board(state_pats_json_r.assert_value())

    turn_pat_json = json_stream.receive_message().assert_value()
    act_pat = ActionPat.from_json(
        turn_pat_json[0]  # pylint: disable=unsubscriptable-object
    )
    offered_tiles: List[Tile] = [
        index_to_tile(tile_idx)
        for tile_idx in turn_pat_json[1:]  # pylint: disable=unsubscriptable-object
    ]
    move = IntermediateMove(
        tile_pattern_to_tile(
            act_pat.tile_pat.tile_index, act_pat.tile_pat.rotation_angle
        ),
        act_pat.player,
    )
    rule_checker = RuleChecker()
    r = rule_checker.validate_move(board.get_board_state(), offered_tiles, move)
    if r.is_error():
        json_stream.send_message("cheating")
    else:
        json_stream.send_message("legal")

    if DEBUG:
        board.get_board_state().debug_display_board()
        r = board.intermediate_move(move)
        if r.is_error():
            print("Failed to render #2")
        else:
            board.get_board_state().debug_display_board()


if __name__ == "__main__":
    main()
