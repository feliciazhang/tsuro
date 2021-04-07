"""
A module containing a class that represents an immutable view of a Tsuro board state. In order to implement an immutable
view of a board state, this class uses pyrsistent for immutable equivalents of python data structures. A board state
is never changed, it is only evolved by calling `with_tile` or `with_live_players`.
"""
import os
from typing import Any, Dict, List, Optional, Tuple

from pyrsistent import pmap
from pyrsistent.typing import PMap

from Common.board_position import (
    MAX_BOARD_COORDINATE,
    MIN_BOARD_COORDINATE,
    BoardPosition,
)
from Common.color import ColorString
from Common.result import Result, error, ok
from Common.tiles import RENDERED_TILE_SIZE, Port, PortID, Tile, port_id_to_network_port_id, tile_to_tile_pattern
from Common.util import random_filename
from Common.validation import validate_types


class BoardState:
    """
    BoardState is a view of the current board state. This class is meant to be shared with player
    strategies and rule checkers. Prior to sharing, it should be deep copied in order to ensure that
    malicious code cannot mutate the game data contained within. Board is the only class that is
    allowed to modify the data internal to BoardState. All other classes must treat BoardState as an
    immutable description of the state of a Tsuro board.
    """

    # board is a list of lists of optional Tile, representing a list of rows on the board. Both the
    # outer list and the nested lists are all required to be of length 10, meaning that the board should
    # be initialized as a List[List[None]].
    _board: PMap[BoardPosition, Tile]

    # live_players is a list of the players (represented by color strings) that are still alive on this
    # board. Specified so that player strategies can determine which pieces are playing and so that the
    # referee can determine the winners based off of who was on the board on the previous tick.
    _live_players: PMap[ColorString, Tuple[BoardPosition, PortID]]

    def __init__(self) -> None:
        self._board = pmap()
        self._live_players = pmap()

    @property
    def board(self) -> PMap[BoardPosition, Tile]:
        """
        Return the board contained within this board state

        :return:    A map from board position to the tile at that board position
        """
        return self._board

    @property
    def live_players(self) -> PMap[ColorString, Tuple[BoardPosition, PortID]]:
        """
        Return the player data contained within this board state

        :return:    A map from a player (represented as a color string) to their position and port
        """
        return self._live_players

    @validate_types
    def get_tile(self, pos: BoardPosition) -> Optional[Tile]:
        """
        Get the tile at the given position if it exists. Otherwise None
        :param pos:     The position to retrieve a tile at
        :return:        Either a tile or none if no tile exists at that position
        """
        return self._board.get(pos, None)

    @validate_types
    def get_position_of_player(
        self, player: ColorString
    ) -> Result[Tuple[BoardPosition, PortID]]:
        """
        Get the position of the player specified by a color. Returns a result containing their position
        on the board and the port they're on, or an error if they are not alive.

        :param player:  The player to retrieve
        :return:        A result containing their position and port or an error
        """
        if player in self._live_players:
            return ok(self._live_players[player])
        return error("player %s is not on the board" % player)

    @validate_types
    def calculate_adjacent_position_of_player(
        self, player: ColorString
    ) -> Result[Optional[BoardPosition]]:
        """
        Calculate the Board Position adjacent to the tile and port that specified player is on.
        :param player:  The color of the player to calculate a position relative to
        :return:        A result containing the board position if the adjacent position is a valid position. None
                        if the adjacent position is off the edge of the board. Or an error.
        """
        if player not in self._live_players:
            return error("player %s is not a live player" % player)
        current_pos_r = self.get_position_of_player(player)
        if current_pos_r.is_error():
            return error(current_pos_r.error())
        current_pos, current_port = (  # pylint: disable=unpacking-non-sequence
            current_pos_r.value()
        )
        if current_port in [Port.TopLeft, Port.TopRight]:
            if current_pos.y - 1 >= 0:
                return ok(BoardPosition(x=current_pos.x, y=current_pos.y - 1))
            else:
                return ok(None)
        elif current_port in [Port.RightTop, Port.RightBottom]:
            if current_pos.x + 1 <= MAX_BOARD_COORDINATE:
                return ok(BoardPosition(x=current_pos.x + 1, y=current_pos.y))
            else:
                return ok(None)
        elif current_port in [Port.BottomLeft, Port.BottomRight]:
            if current_pos.y + 1 <= MAX_BOARD_COORDINATE:
                return ok(BoardPosition(x=current_pos.x, y=current_pos.y + 1))
            else:
                return ok(None)
        elif current_port in [Port.LeftBottom, Port.LeftTop]:
            if current_pos.x - 1 >= MIN_BOARD_COORDINATE:
                return ok(BoardPosition(x=current_pos.x - 1, y=current_pos.y))
            else:
                return ok(None)
        else:
            return error(
                "could not match current_port %s to a direction" % current_port
            )

    @validate_types
    def surrounding_positions_are_empty(self, pos: BoardPosition) -> bool:
        """
        Returns whether the positions surrounding (in the 4 cardinal directions) the given position are all empty.

        :param pos:     The position to check
        :return:        Whether the cardinal positions are all empty
        """
        if (
            pos.y - 1 >= MIN_BOARD_COORDINATE
            and self.get_tile(BoardPosition(pos.x, pos.y - 1)) is not None
        ):
            return False
        if (
            pos.x - 1 >= MIN_BOARD_COORDINATE
            and self.get_tile(BoardPosition(pos.x - 1, pos.y)) is not None
        ):
            return False
        if (
            pos.y + 1 <= MAX_BOARD_COORDINATE
            and self.get_tile(BoardPosition(pos.x, pos.y + 1)) is not None
        ):
            return False
        if (
            pos.x + 1 <= MAX_BOARD_COORDINATE
            and self.get_tile(BoardPosition(pos.x + 1, pos.y)) is not None
        ):
            return False
        return True

    @validate_types
    def port_faces_interior(  # pylint: disable=no-self-use
        self, pos: BoardPosition, port: PortID
    ) -> bool:
        """
        Returns whether the given port on the given position faces the interior of the board

        :param pos:     The position to check
        :param port:    The port ID to check
        :return:        True if it faces the interior of the board or is on the interior of the board
        """
        if pos.x == MIN_BOARD_COORDINATE and port in [Port.LeftTop, Port.LeftBottom]:
            return False
        if pos.y == MIN_BOARD_COORDINATE and port in [Port.TopLeft, Port.TopRight]:
            return False
        if pos.x == MAX_BOARD_COORDINATE and port in [Port.RightBottom, Port.RightTop]:
            return False
        if pos.y == MAX_BOARD_COORDINATE and port in [
            Port.BottomRight,
            Port.BottomLeft,
        ]:
            return False
        return True

    @validate_types
    def to_html(self, automatic_refresh: bool = False) -> str:
        """
        Convert this board state to HTML that can be used to display it in the browser

        :param automatic_refresh:   If True, have the HTML automatically reload every 1 second
        :return:                    A string containing valid HTML that will render this board state (including
                                    the live players) in a web browser.
        """
        lines = []
        for y in range(MIN_BOARD_COORDINATE, MAX_BOARD_COORDINATE + 1):
            row = []
            for x in range(MIN_BOARD_COORDINATE, MAX_BOARD_COORDINATE + 1):
                tile = self._board.get(BoardPosition(x, y), None)
                if tile is None:
                    row.append("<div class='blank' ></div>")
                else:
                    port_to_player: Dict[PortID, List[ColorString]] = {}
                    for player, (pos, port) in self._live_players.items():
                        if port not in port_to_player:
                            port_to_player[port] = []
                        if pos.x == x and pos.y == y:
                            port_to_player[port].append(player)
                    row.append(tile.to_svg(players=port_to_player))
            lines.append("<div style='display:flex'>%s</div>" % "\n".join(row))
        return f"""
%s
<style>
    body {{
        width: 10000px;
    }}
    .img {{
        width: {RENDERED_TILE_SIZE}px;
        height: {RENDERED_TILE_SIZE}px;
        margin: 0px;
        padding: 0px;
    }}
    .blank {{
        width: {RENDERED_TILE_SIZE}px;
        height: {RENDERED_TILE_SIZE}px;
        background-color: gray;
        margin: 0px;
        padding: 0px;
        display: inline-block;
    }}
</style>

%s
""" % (
            '<meta http-equiv="refresh" content="1" />' if automatic_refresh else "",
            "\n".join(lines),
        )

    def to_state_pats(self) -> List:
        """
        Turn the given board state into a list of state-pats as defined in assignment 4
        https://felleisen.org/matthias/4500-f19/4.html#%28tech._state._pat%29

        :return:            A list of state-pats representing the current state of all tiles and avatars
                            on the board
        """
        return self.players_to_intial_place() + self.board_to_intermediate_place()

    def board_to_intermediate_place(self) -> List[List]:
        """
        Get the list of intermediate-places for tiles on the board without players per the definition in
        https://felleisen.org/matthias/4500-f19/4.html#%28tech._state._pat%29

        :return:            A list of intermediate_place representing the current state of all tiles without
                            players on the board
        """
        player_tile_posns = [player[1][0] for player in self._live_players.items()]
        return [self.tile_to_intermediate(board_tile)
            for board_tile in self._board.items() if board_tile[0] not in player_tile_posns]

    def tile_to_intermediate(self, board_tile) -> List:
        """
        Get the intermediate-place for a single tile on the board per the definition in
        https://felleisen.org/matthias/4500-f19/4.html#%28tech._state._pat%29

        :return:            An intermediate representing the current state of the given tile
        """
        tile_posn = board_tile[0]
        tile_pat = tile_to_tile_pattern(board_tile[1])

        return [tile_pat, tile_posn.x, tile_posn.y]

    
    def players_to_intial_place(self) -> List[List]:
        """
        Get the list of inital-places for all the live players on the board per the definition in
        https://felleisen.org/matthias/4500-f19/4.html#%28tech._state._pat%29

        :return:            A list of initial_place representing the current state of all tiles with avatars
                            on the board
        """
        return [self.player_to_initial(player) for player in self._live_players.items()]

    def player_to_initial(self, player) -> List:
        """
        Get the initial-place for a single live player on the board per the definition in
        https://felleisen.org/matthias/4500-f19/4.html#%28tech._state._pat%29

        :return:            An initial_place representing the current state of the given live player
        """
        player_color = player[0]
        player_posn = player[1][0]
        player_port = port_id_to_network_port_id(player[1][1])

        return [tile_to_tile_pattern(self._board[player_posn]), player_color, player_port, player_posn.x, player_posn.y]
        
    def debug_display_board(self) -> None:
        """
        Attempt to display the graphical representation of this board state in google-chrome. Meant
        to be used for debugging purposes only.

        :return: None
        """
        filename = random_filename() + ".html"
        with open(filename, "w") as file:
            file.write(self.to_html())
    
        print("Opening %s in google-chrome..." % filename)
        os.system("google-chrome %s" % filename)

    def with_tile(self, tile: Tile, pos: BoardPosition) -> "BoardState":
        """
        Create a new board state by evolving this board state by placing the given tile at the given position

        :param tile:    The tile to place
        :param pos:     The position to place it at
        :return:        A new board state with the placed tile
        """
        return self.with_change(added_tile_pos=(tile, pos))

    def with_live_players(
        self, new_live_players: PMap[ColorString, Tuple[BoardPosition, PortID]]
    ) -> "BoardState":
        """
        Create a new board state by evolving this board state by setting the players data structure to the given one

        :param new_live_players:    The new set of live players
        :return:                    A new board state with the placed tile
        """
        return self.with_change(new_live_players=new_live_players)

    def with_change(
        self,
        added_tile_pos: Optional[Tuple[Tile, BoardPosition]] = None,
        new_live_players: Optional[
            PMap[ColorString, Tuple[BoardPosition, PortID]]
        ] = None,
    ) -> "BoardState":
        """
        Create a new board state by evolving this board state with the given change. Does not validate the
        given change.

        :param added_tile_pos:      The tile to be added at the given position
        :param new_live_players:    The new map from player to position, port
        :return:                    A new board state with the requested data set inside of it
        """
        new_board = self._board
        if added_tile_pos:
            tile, pos = added_tile_pos
            new_board = self._board.set(pos, tile)
        if new_live_players is None:
            new_live_players = self._live_players
        board_state = BoardState()
        board_state._live_players = new_live_players  # pylint: disable=protected-access
        board_state._board = new_board  # pylint: disable=protected-access
        return board_state

    def __deepcopy__(self, memo: Any) -> "BoardState":
        # Create a deep copy of itself. Abides by the standards set forth by Python 3's copy.deepcopy().
        return self

    def __eq__(self, other: Any) -> bool:
        if isinstance(other, BoardState):
            return (
                self._board == other._board  # pylint: disable=protected-access
                and self._live_players
                == other._live_players  # pylint: disable=protected-access
            )
        return False

    def __hash__(self) -> int:
        return hash((tuple(self._board.items()), tuple(self._live_players.items())))
