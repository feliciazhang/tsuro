from Admin.administrator import Administrator
from Admin.bracket_strategy import SimpleBracketStrategy
from Common.json_stream import NetworkJSONStream, StdinStdoutJSONStream
from Common.result import Result
from Common.util import timeout
from Remote.remote_player import RemotePlayer
from typing import List

TIMEOUT_SECONDS = 60
MAX_PLAYERS = 20

class Server():
    """
    Represents the Tsuro Game server that can be connected to by clients via
    TCP and constructs an Administrator to run a tournament.
    """
    def __init__(self, port: int, names: List[str]):
        self._admin = Administrator(SimpleBracketStrategy())
        self._names = names
        self._players = {}
        try:
            with timeout(seconds = TIMEOUT_SECONDS):
                self.connect_players(port)
        except:
            pass # after a minute, start the tournament
        r_tournament = self._admin.run_tournament()
        self.print_tournament_results(r_tournament)

    def connect_players(self, port: int):
        """
        Creates TCP connections with player clients at the given port and creates a list of remote players.
        """
        host = "127.0.0.1"
        port = int(port)
        
        njs = NetworkJSONStream(host, port)
        njs.sock.bind((host, port))
        njs.sock.listen(MAX_PLAYERS)

        while(len(self._players) < MAX_PLAYERS):
            conn, _ = njs.sock.accept()
            player = RemotePlayer(conn)
            r_pid = self._admin.add_player(player)
            if (r_pid.is_ok()):
              
                self._players[r_pid.value()] = self._names[len(self._players)]
                

    def print_tournament_results(self, r_tournament: Result) -> None:
        """
        Prints the winners and cheaters in the tournament results in sorted order by player id
        """
        winners = [sorted([self._players[winner] for winner in winner_set]) for winner_set in r_tournament.assert_value()[0]]
        cheaters = [self._players[cheater] for cheater in r_tournament.assert_value()[1]]

        message = {
            "winners": winners,
            "cheaters": sorted(cheaters)
        } if len(cheaters) > 0 else {
            "winners": winners
        }
        json_stream = StdinStdoutJSONStream()
        json_stream.send_message(message)

       
    