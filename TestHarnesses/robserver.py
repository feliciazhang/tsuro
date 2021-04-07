"""
An implementation for the experimentation task in Assignment 5. Connects to a remote server, receives
board state, and renders it via a GUI. Run via `python3.6 robserver.py 1.2.3.4 5678`.
"""
import sys
from typing import List

from Common.action import ActionPat
from Common.constants import AUTHORS
from Common.json_stream import NetworkJSONStream
from Common.moves import IntermediateMove
from Common.tiles import Tile, index_to_tile, tile_pattern_to_tile
from Player.player_observer import GraphicalPlayerObserver
from TestHarnesses.xboard import setup_board


def main(host: str, port: int) -> None:
    """
    Connect to the server at host:port via TCP to render a board state to the GUI via a GraphicalPlayerObserver
    :param host:    The host to connect to
    :param port:    The port to connect to
    :return:        None
    """
    gpo = GraphicalPlayerObserver()

    json_stream = NetworkJSONStream.tcp_client_to(host, port)
    json_stream.send_message(AUTHORS)

    state_pats_json_r = json_stream.receive_message()
    board = setup_board(state_pats_json_r.assert_value())
    gpo.set_players(list(board.live_players.keys()))

    turn_pat_json = json_stream.receive_message().assert_value()
    act_pat = ActionPat.from_json(
        turn_pat_json[0]  # pylint: disable=unsubscriptable-object
    )
    gpo.set_color(act_pat.player)
    offered_tiles: List[Tile] = [
        index_to_tile(tile_idx) for tile_idx in turn_pat_json[1:]
    ]
    gpo.intermediate_move_offered(offered_tiles, board.get_board_state())
    move = IntermediateMove(
        tile_pattern_to_tile(
            act_pat.tile_pat.tile_index, act_pat.tile_pat.rotation_angle
        ),
        act_pat.player,
    )
    gpo.intermediate_move_played(offered_tiles, board.get_board_state(), move)
    json_stream.close()


if __name__ == "__main__":
    main(sys.argv[1], int(sys.argv[2]))
