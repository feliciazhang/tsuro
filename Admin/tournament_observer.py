from typing import Set, Dict, Tuple
import logging
import subprocess
import time
from copy import deepcopy
from multiprocessing import Queue  # pylint: disable=unused-import

from Admin.administrator import PlayerID, TournamentLeaderboard 
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
OUT = "out"

STARTING_AGE = 20

class TournamentObserver:
    def __init__(self) -> None:
        """
        Make a new TournamentObserver. A given instance of TournamentObserver should only be added to a
        single tournament at a time.
        """
        # Start the websocket server that is used to trigger refreshes after changes
        self._websocket_message_queue: "Queue[str]" = start_websocket_distributor()

        self._filename = "tournament_observer.html"
        self._round_number = 0
        self._current_game: Set(str) = set()
        self._players: Dict[str, Tuple[int, str]] = {} # playerid to (age, PlayerStatus)
        self._games: Set[Set[PlayerID]] = set()
        self._render_update()
        #Run with no output to the terminal
        subprocess.run(
            ["open", "-a", "Google Chrome", self._filename],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )


    @validate_types
    def _render_update(self, results= None) -> None:
        """
        Render the given board state to the filename such that it will be updated in the user's browser
        :param board_state:     The board state to render
        """
        with open(self._filename, "w") as file:
            file.write(self._make_tournament_state(results))
            file.write(self._make_websocket_refresher())
        self._websocket_message_queue.put("REFRESH")
        time.sleep(0.5)

    @validate_types
    def _make_tournament_state(self, results= None) -> str:
        round_title = "Round " + str(self._round_number) if self._round_number > 0 else ""
        column_header = round_title if results == None else "Tournament results:"

        return """
        <div style="display: flex">
            <div>
                <ul>
                    <li>
                        <span class="player-age"><b>Player age</b></span>
                        <span class="player-status"><b>Player status</b></span>
                    </li>
                    {}
                </ul>
            </div>
            <div>
                <h3>{}</h3>
                <ul>
                    {}
                </ul>
            </div>
        </div>
        <style>
            ul {{
                margin: 20px;
                list-style-type: none;
                padding-inline-start: 0;
                padding: 8px;
            }}
            h3 {{
                text-align: center;
            }}
            .player-age,
            .player-status {{
                width: 100px;
                padding: 10px;
                border: 1px solid pink;
                display: inline-block;
            }}
        </style>
        """.format(
            self._make_player_list(),
            column_header,
            self._make_games() if results == None else self._make_results(results)
        )

    @validate_types
    def _make_results(self, results) -> str:
        winners = "\n".join([
            f"""
                <div>
                Rank {idx + 1}: 
                {", ".join([str(self._players[player][0]) for player in rank])}
                </div>
            """
            for idx, rank in enumerate(results[0])
        ])
        cheaters = ", ".join(
            [str(self._players[player][0]) for player in results[1]]
        )
        return f"""
            <div>
                {winners}
            </div>
            <div>
                Cheaters: {cheaters}
            </div>
            """
    
    @validate_types
    def _make_player_list(self) -> str:
        return "\n".join(
                [
                    f"""
                    <li>
                        <span class="player-age">{player[0]}</span>
                        <span class="player-status">{player[1]}</span>
                    </li>
                    """
                    for player in self._players.values()
                ]
            )

    @validate_types
    def _make_games(self) -> str:
        return "\n".join(
                [
                    f"""
                    <li><ul style="border: 3px solid {"blue" if game == self._current_game else "black"}">
                        {self._make_single_game(game)}
                    </ul></li>
                    """
                    for game in self._games
                ]
            )

    @validate_types
    def _make_single_game(self, game: Set[PlayerID]) -> str:
        return "\n".join(
                [
                    f"""
                    <li>{self._players[player][0]}</li>
                    """
                    for player in game
                ]
            )

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
    
    def player_added(self, player_id: PlayerID) -> None:
        """
        An observer method that is called to describe when a player is added to the game. Provides the
        player ID that the player was assigned by the administrator. The player's join time is used to
        determine their age which determines the order in which they play in individual Tsuro games.

        :param player_id:   The player ID of the added player
        :param player_age:  The age of the added player
        """
   
        self._players[player_id] = (STARTING_AGE - len(self._players.items()), ACTIVE)
        self._render_update()
        
    def games_created(self, games: Set[Set[PlayerID]]) -> None:
        """
        An observer method that is called to describe when a set of games is created by the
        BracketStrategy. A game is represented as a set of 3-5 player IDs that will play against each
        other in a single game of Tsuro. Thus, multiple games are represented as a set of games. This
        observer method is called prior to the individual game being executed by a referee.
        
        :param games:  The set of games that have been created
        """
        self._games = games
        self._round_number += 1
        self._render_update()

    def game_started(self, game: Set[PlayerID]) -> None:
        """
        An observer method that is called to describe when an individual Tsuro game is started.
        
        :param game:        The set of players that played in the game
        """
        self._current_game = game
        self._render_update()
        
    def game_completed(self, game: Set[PlayerID], game_result: TournamentLeaderboard) -> None:
        """
        An observer method that is called to describe when an individual Tsuro game is completed.
        Provides the players that played in the game and the game result. Note that the game_result is
        of type TournamentLeaderboard so that is uses the same player IDs that the observer is provided.
        
        :param game:        The set of players that played in the game
        :param results:     The results of the individual game
        """
        self._current_game = set()
        self._render_update()
        
    def players_eliminated(self, eliminated_players: Set[PlayerID]) -> None:
        """
        An observer method that is called to describe when players are eliminated from a Tsuro
        tournament by the administrator's bracket strategy. To be precise, this type of elimination is
        based off of player's performance in individual Tsuro games. If a player is removed for
        cheating, this method is not called. It is guaranteed that a player can only be eliminated a
        single time.
        
        :param eliminated_players:  The set of players eliminated from the tournament
        """
        for player in eliminated_players:
            self._players[player] = (self._players[player][0], OUT)
        self._render_update()
        
    def player_cheated(self, player: PlayerID) -> None:
        """
        An observer method that is called to describe when a player is removed from the tournament for
        cheating.
        
        :param player:  The player ID of the player that attempted to cheat
        """
        self._players[player] = (self._players[player][0], OUT)
        self._render_update()
        
    def tournament_completed(self, leaderboard: TournamentLeaderboard) -> None:
        """
        An observer method that is called to describe when a Tsuro tournament is completed. Provides
        the complete leaderboard of the completed Tsuro tournament.
        
        :param leaderboard:     The leaderboard of the completed Tsuro tournament
        """
        winners = leaderboard[0][0]
        for player_id in self._players.keys():
            if player_id not in list(winners):
                self._players[player_id] = (self._players[player_id][0], OUT)
        self._render_update(results=leaderboard)
    

