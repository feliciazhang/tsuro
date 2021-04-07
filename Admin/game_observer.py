from typing import List
import logging
import subprocess
import time
from typing import List, Optional, Tuple, Dict
from copy import deepcopy
from multiprocessing import Queue  # pylint: disable=unused-import
from pynput import keyboard

from Common.tsuro_types import GameResult
from Common.color import ColorString
from Common.moves import InitialMove, IntermediateMove
from Common.rules import EXPECTED_TILE_COUNT_INITIAL_MOVE
from Common.board import Board
from Common.board import BoardState                                 # See Planning/board.md
from Common.tiles import Tile                                       # See Planning/board.md
from Common.validation import validate_types
import Common.tiles as T
from Player.gui_websocket_server import start_websocket_distributor

# PlayerStatus
ACTIVE = "active"
CHEATED = "cheated"
LOST = "lost"

# Represents an observer for a game, which can observe which players are still in the game, which player is the acting player, and which action the player has chosen to take in a graphical form.
class RefereeObserver:

    def __init__(self) -> None:
        """
        Make a new GameObserver. A given instance of GameObserver should only be added to a
        single game a time.
        """
        # Start the websocket server that is used to trigger refreshes after changes
        self._websocket_message_queue: "Queue[str]" = start_websocket_distributor()

        self._filename = "game_observer.html"
        self._most_recent_board_state: BoardState = BoardState()
        self._current_player_color: Optional[ColorString] = None
        self._players: Dict[ColorString, str] = {}
        self._states = list()
        self._current_state = 0
        self._render_update()
        
        #Run with no output to the terminal
        subprocess.run(
            ["open", "-a", "Google Chrome", self._filename],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
       
    @validate_types
    def _render_update(self, tile_choices: Optional[List[Tile]] = None, chosen_tile: Optional[Tile] = None, results:GameResult = None) -> None:
        """
        Render the given board state to the filename such that it will be updated in the user's browser
        :param board_state:     The board state to render
        """
        file_string = self._make_header(tile_choices, chosen_tile, results=results) + self._most_recent_board_state.to_html(automatic_refresh=False) + self._make_websocket_refresher()
        self._states.append(file_string)
        self._current_state += 1
        self._render_state()
        time.sleep(0.5)

    def _render_state(self):
        with open(self._filename, "w") as file:
            file.write(self._states[self._current_state - 1])

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
    def _make_header(self, tile_choices: Optional[List[Tile]] = None, chosen_tile: Optional[Tile] = None, results:GameResult = None) -> str:
        """
        Renders the results of the game with all winners ranks and cheaters
        """
        if tile_choices is None:
            tile_choices = []
        assert len(tile_choices) <= EXPECTED_TILE_COUNT_INITIAL_MOVE
        tile_htmls = self._get_tile_options_html(tile_choices, chosen_tile)

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
            self._make_results(results) if results != None else self._make_player_list(),
        )

    @validate_types
    def _make_results(self, results: GameResult) -> str:
  
        winners = "\n".join([
            f"""
                <div class="winner-rank">
                Rank {idx + 1}: 
                {", ".join([player for player in rank])}
                </div>
            """
            for idx, rank in enumerate(results[0])
        ])
        cheaters = ", ".join(
            [player for player in results[1]]
        )
        return f"""
            <div class="winners">
                {winners}
            </div>
            <div class="cheaters">
                Cheaters: {cheaters}
            </div>
            <style>
                .winners,
                .cheaters {{
                    margin: 16px 16px 0;
                    display: block;
                }}
            </style>
            """

    @validate_types
    def _get_tile_options_html(self, tile_choices: Optional[List[Tile]] = None,
        chosen_tile: Optional[Tile] = None ) -> str:
        tile_htmls: List[str] = []
        for tile in tile_choices:
            border_style = "3px solid black" if chosen_tile and T.tile_to_index(tile) == T.tile_to_index(chosen_tile) else "none"
            tile_htmls.append("<div style='display: inline-block; border: {}'>{}</div>".format(border_style, tile.to_svg()))
        tile_htmls += ["<div class='blank' ></div>"] * (
            EXPECTED_TILE_COUNT_INITIAL_MOVE - len(tile_choices)
        )
        return tile_htmls

    @validate_types
    def _make_player_list(self) -> str:
        return """
        <div>
            <ul>
                {}
            </ul>
        </div>
        <style>
            body {{
                overflow-x: hidden;
            }}
            ul {{
                margin: 20px;
                list-style-type: none;
            }}
            .player-label {{
                width: 100%;
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
        """.format(
            self._get_player_list_items()
        )

    @validate_types
    def _get_player_list_items(self) -> str:
        return "\n".join(
                [
                    f"""<li>
                    <div class="input-color">
                        <input class="player-label" readonly="true" type="text"
                               value="{self._get_player_status(player)}" />
                        <div class="color-box" style="background-color: {player}; border: 1px solid black;"></div>
                    </div>
                </li>"""
                    for player in sorted(self._players.keys())
                ]
            )
    
    @validate_types
    def _get_player_status(self, player: ColorString) -> str:
        if player == self._current_player_color:
            return "currently taking turn"
        else:
            return self._players[player]

    def players_added(self, players: List[ColorString]) -> None:
        """
        An observer method that is called to describe when players are added to the game. The list is
        ordered by age descending.

        :param players:         The list of player avatars that were added to the game
        """
        for player in players:
            self._players[player] = ACTIVE
       
    def game_completed(self, leaderboard: GameResult) -> None:
        """
        An observer method that is called at the end of game to deliver the game result to the referee
        observer.
        
        :param leaderboard:     The results of the completed game
        """
        self._current_player_color = None
        self._render_update()

    def initial_move_offered(
        self, player: ColorString, tiles: List[Tile], board_state: BoardState
    ) -> None:
        """
        An observer method that is called to describe when a player is prompted for an initial move and
        the data that is given to them when they are prompted for an initial move.

        :param player:          The player who is being asked for a move
        :param tiles:           The list of tiles that the player is allowed to choose between
        :param board_state:     The board state that the player is playing against
        """
        self._current_player_color = player
        self._render_update(tiles)

    def initial_move_played(
        self, player: ColorString, tiles: List[Tile], board_state: BoardState, move: InitialMove
    ) -> None:
        """
        An observer method that is called to describe when a player returns an initial move to be placed

        :param player:          The player who is being asked for a move
        :param tiles:           The list of tiles that the player is allowed to choose between
        :param board_state:     The board state that the player is playing against
        :param move:            The initial move that the player placed on the board
        """
        self._current_player_color = player
        board = Board(deepcopy(board_state))
        r = board.initial_move(move)
        if r.is_ok():
            self._most_recent_board_state = board.get_board_state()
            self._render_update(tiles, move.tile)
        else:
            logging.warning(
                "GameObserver.initial_move_played failed to render updated board after "
                "an initial move because the given initial move is invalid. Ignoring..."
            )

    def intermediate_move_offered(
        self, player: ColorString, tiles: List[Tile], board_state: BoardState
    ) -> None:
        """
        An observer method that is called to describe when a player is prompted for an intermediate move
        and the data that is given to them when they are prompted for an intermediate move.

        :param player:          The player who is being asked for a move
        :param tiles:           The list of tiles that the player is allowed to choose between
        :param board_state:     The board state that the player is playing against
        """
        self._current_player_color = player
        self._render_update(tiles)

    def intermediate_move_played(
        self, player: ColorString, tiles: List[Tile], board_state: BoardState, move: IntermediateMove, validMove: bool) -> None:
        """
        An observer method that is called to describe when a player returns an intermediate move to be
        placed.

        :param player:          The player who is being asked for a move
        :param tiles:           The list of tiles that the player is allowed to choose between
        :param board_state:     The board state that the player is playing against
        :param move:            The intermediate move that the player placed on the board
        """
        self._current_player_color = player
        board = Board(deepcopy(board_state))
        r = board.intermediate_move(move)
        if r.is_ok() and validMove:
            self._most_recent_board_state = board.get_board_state()
            self._render_update(tiles, move.tile)
        elif r.is_ok():
            self._render_update(tiles, move.tile)
        else:
            logging.warning(
                "GameObserver.intermediate_move_played failed to render updated board after "
                "an intermediate move because the given intermediate move is invalid. Ignoring..."
            )

    def cheater_removed(self, cheater: ColorString, board_state: BoardState) -> None:
        """
        An observer method that is called to describe when a player is removed for cheating.

        :param cheater:          The player who was removed for cheating
        """
        self._current_player_color = None
        self._players[cheater] = CHEATED
        self._most_recent_board_state = board_state
        self._render_update()

    def player_eliminated(self, loser: ColorString, board_state: BoardState) -> None:
        """
        An observer method that is called to describe when a player is eliminated due to moving off of
        the board or being killed by a loop

        :param loser           The player who was eliminated when moved off the board
        """
        self._current_player_color = None
        self._players[loser] = LOST
        self._most_recent_board_state = board_state
        self._render_update()

    def game_result(self, game_result: GameResult) -> None:
        """
        An observer method that is called when the game of Tsuro is complete.

        :param game_result:     The game results
        """
        self._current_player_color = None
        self.listen_to_keyboard()
        self._render_update(results=game_result)

    def listen_to_keyboard(self):
        '''
        Use the left and right arrow keys to go through the history
        of a game.
        '''
        def on_press(key):
            if key == keyboard.Key.left:
                if self._current_state > 0:
                    self._current_state -= 1
                    self._render_state()
            if key == keyboard.Key.right:
                if self._current_state < len(self._states):
                    self._current_state += 1
                    self._render_state()
            if key == keyboard.Key.backspace:
                self._current_state = 1
                self._render_state()
            
        # Collect events until released
        listener = keyboard.Listener(
                on_press=on_press)
                
        listener.start()
