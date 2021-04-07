"""
A player observer that renders the updated board as the player receives the updated board.

Meant to be imported and used from player_observer.py (not player-observer.py which is included in the
Player directory solely to meet the requirements of Assignment 5). Note that player_observer.py is a symlink
to player-observer.py.
"""

import logging
import subprocess
from copy import deepcopy
from multiprocessing import Queue  # pylint: disable=unused-import
from typing import List, Optional, Tuple

from Common.board import Board
from Common.board_state import BoardState
from Common.color import ColorString
from Common.moves import InitialMove, IntermediateMove
from Common.rules import EXPECTED_TILE_COUNT_INITIAL_MOVE
from Common.tiles import Tile
from Common.tsuro_types import GameResult
from Common.util import random_filename
from Common.validation import validate_types
from Player.gui_websocket_server import start_websocket_distributor
from Player.observer_interface import PlayerObserver


class GraphicalPlayerObserver(PlayerObserver):
    """
    A player observer that renders the board state to a GUI via the default web browser installed on the system
    """

    def __init__(self) -> None:
        """
        Make a new GraphicalPlayerObserver. A given instance of GraphicalPlayerObserver should only be added to a
        single player at a time.
        """
        # Start the websocket server that is used to trigger refreshes after changes
        self._websocket_message_queue: "Queue[str]" = start_websocket_distributor()

        self._filename = random_filename() + ".html"
        self._most_recent_board_state: BoardState = BoardState()
        self._player_color: Optional[ColorString] = None
        self._players: List[ColorString] = []
        self._render_update()
        # Run with no output to the terminal
        subprocess.run(
            ["google-chrome", self._filename],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )

    @validate_types
    def _render_update(self, tile_choices: Optional[List[Tile]] = None) -> None:
        """
        Render the given board state to the filename such that it will be updated in the user's browser
        :param board_state:     The board state to render
        """
        with open(self._filename, "w") as file:
            file.write(self._make_header(tile_choices))
            file.write(self._most_recent_board_state.to_html(automatic_refresh=False))
            file.write(GraphicalPlayerObserver._make_websocket_refresher())
        self._websocket_message_queue.put("REFRESH")

    @staticmethod
    @validate_types
    def _make_websocket_refresher() -> str:
        return """
        <script>
        let socket = new WebSocket("ws://localhost:8765");
        socket.onopen = function(e) {
            console.log("[open] Connection established");
        };
        socket.onmessage = function(event) {
            console.log(`[message] Data received from server: ${event.data}`);
            window.location.reload()
        };
        socket.onclose = function(event) {
            if (event.wasClean) {
                console.log(`[close] Connection closed cleanly, code=${event.code} reason=${event.reason}`);
            } else {
                console.log('[close] Connection died');
            }
            // Reload 500ms after a socket closes 
            setTimeout(function() {window.location.reload()}, 500);
        };
        </script>
        """

    @validate_types
    def _make_header(self, tile_choices: Optional[List[Tile]] = None) -> str:
        if tile_choices is None:
            tile_choices = []
        assert len(tile_choices) <= EXPECTED_TILE_COUNT_INITIAL_MOVE
        tile_htmls: List[str] = []
        for tile in tile_choices:
            tile_htmls.append(tile.to_svg())
        tile_htmls += ["<div class='blank' ></div>"] * (
            EXPECTED_TILE_COUNT_INITIAL_MOVE - len(tile_choices)
        )

        return """
        <div style="display: flex">
            <div>
            %s
            </div>
            %s
        </div>
        <br/>
        """ % (
            "\n".join(tile_htmls),
            self._make_player_list(),
        )

    @validate_types
    def _make_player_list(self) -> str:
        return f"""
        <div>
            <ul>
                <li>
                    <div class="input-color">
                        <input class="current_player player-label" type="text" readonly="true" value="Current Player" />
                        <div class="color-box" style="background-color: {self._player_color}; border: 1px solid black;"></div>
                    </div>
                </li>
                %s
            </ul>
        </div>
        <style>
            ul {{
                margin: 20px;
                list-style-type: none;
            }}
            .current_player {{
                font-weight: bold;
            }}
            .player-label {{
                width: 100%%;
            }}
            .input-color {{
                position: relative;
            }}
            .input-color input {{
                padding-left: 20px;
            }}
            .input-color .color-box {{
                width: 10px;
                height: 10px;
                display: inline-block;
                background-color: #ccc;
                position: absolute;
                left: 5px;
                top: 5px;
            }}
        </style>
        """ % (
            "\n".join(
                [
                    f"""<li>
                    <div class="input-color">
                        <input class="player-label" readonly="true" type="text"
                               value="{self._get_player_status(player)}" />
                        <div class="color-box" style="background-color: {player}; border: 1px solid black;"></div>
                    </div>
                </li>"""
                    for player in sorted(self._players)
                    if player != self._player_color
                ]
            )
        )

    @validate_types
    def _get_player_status(self, player: ColorString) -> str:
        if player in self._most_recent_board_state.live_players:
            return "Alive"
        else:
            return "Dead"

    @validate_types
    def set_color(self, color: ColorString) -> None:
        self._player_color = color

    @validate_types
    def set_players(self, players: List[ColorString]) -> None:
        self._players = players

    @validate_types
    def initial_move_offered(self, tiles: List[Tile], board_state: BoardState) -> None:
        """
        Render the game state when the player is prompted for an initial move

        :param tiles:           The list of tiles that the player is allowed to choose between
        :param board_state:     The board state that the player is playing against
        """
        self._render_update(tiles)

    @validate_types
    def initial_move_played(
        self, tiles: List[Tile], board_state: BoardState, move: InitialMove
    ) -> None:
        """
        Render the game state after the player's move to the user's web browser

        :param tiles:           Not used
        :param board_state:     Rendered to the user
        :param move:            Not used
        """
        board = Board(deepcopy(board_state))
        r = board.initial_move(move)
        if r.is_ok():
            self._most_recent_board_state = board.get_board_state()
            self._render_update()
        else:
            logging.warning(
                "GraphicalPlayerObserver.initial_move_played failed to render updated board after "
                "an initial move because the given initial move is invalid. Ignoring..."
            )

    @validate_types
    def intermediate_move_offered(
        self, tiles: List[Tile], board_state: BoardState
    ) -> None:
        """
        Render the game state when the player is prompted for an intermediate move

        :param tiles:           The list of tiles that the player is allowed to choose between
        :param board_state:     The board state that the player is playing against
        """
        self._render_update(tiles)

    @validate_types
    def intermediate_move_played(
        self, tiles: List[Tile], board_state: BoardState, move: IntermediateMove
    ) -> None:
        """
        Render the game state after the player's move to the user's web browser

        :param tiles:           Not used
        :param board_state:     Rendered to the user
        :param move:            Not used
        """
        board = Board(deepcopy(board_state))
        r = board.intermediate_move(move)
        if r.is_ok():
            self._most_recent_board_state = board.get_board_state()
            self._render_update()
        else:
            logging.warning(
                "GraphicalPlayerObserver.intermediate_move_played failed to render updated board after "
                "an intermediate move because the given intermediate move is invalid. Ignoring..."
            )


class LoggingPlayerObserver(PlayerObserver):
    """
    A logging player observer that logs all observed method calls to internal arrays
    """

    def __init__(self) -> None:
        self.set_colors: List[ColorString] = []
        self.set_playerss: List[List[ColorString]] = []
        self.initial_move_offereds: List[Tuple[List[Tile], BoardState]] = []
        self.initial_move_playeds: List[Tuple[List[Tile], BoardState, InitialMove]] = []
        self.intermediate_move_offereds: List[Tuple[List[Tile], BoardState]] = []
        self.intermediate_move_playeds: List[
            Tuple[List[Tile], BoardState, IntermediateMove]
        ] = []
        self.game_results: List[GameResult] = []

    def set_color(self, color: ColorString) -> None:
        """
        An observer method that is called once at the start of a game to set the color
        that the observed player is playing as

        :param color:   The color that the player is playing as
        """
        self.set_colors.append(color)

    def set_players(self, players: List[ColorString]) -> None:
        """
        An observer method that is called once at the start of a game to set the list of players that are
        playing in a given game.

        :param players:     The list of players represented as a list of colors
        """
        self.set_playerss.append(players)

    def initial_move_offered(self, tiles: List[Tile], board_state: BoardState) -> None:
        """
        An observer method that is called to describe when a player is prompted for an initial move and the data
        that is given to them when they are prompted for an initial move.

        :param tiles:           The list of tiles that the player is allowed to choose between
        :param board_state:     The board state that the player is playing against
        """
        self.initial_move_offereds.append((tiles, board_state))

    def initial_move_played(
        self, tiles: List[Tile], board_state: BoardState, move: InitialMove
    ) -> None:
        """
        An observer method that is called to describe when a player returns an initial move to be placed.

        :param tiles:           The list of tiles that the player is allowed to choose between
        :param board_state:     The board state that the player is playing against
        :param move:            The initial move that the player placed on the board
        """
        self.initial_move_playeds.append((tiles, board_state, move))

    def intermediate_move_offered(
        self, tiles: List[Tile], board_state: BoardState
    ) -> None:
        """
        An observer method that is called to describe when a player is prompted for an intermediate move and the data
        that is given to them when they are prompted for an intermediate move.

        :param tiles:           The list of tiles that the player is allowed to choose between
        :param board_state:     The board state that the player is playing against
        """
        self.intermediate_move_offereds.append((tiles, board_state))

    def intermediate_move_played(
        self, tiles: List[Tile], board_state: BoardState, move: IntermediateMove
    ) -> None:
        """
        An observer method that is called to describe when a player returns an intermediate move to be placed.

        :param tiles:           The list of tiles that the player is allowed to choose between
        :param board_state:     The board state that the player is playing against
        :param move:            The intermediate move that the player placed on the board
        """
        self.intermediate_move_playeds.append((tiles, board_state, move))

    def game_result(self, result: GameResult) -> None:
        """
        An observer method that is called to describe when a player is given the game results after a game of Tsuro
        is completed.

        :param result:  The game results
        """
        self.game_results.append(result)
