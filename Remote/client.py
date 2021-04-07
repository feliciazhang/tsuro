from Player.player import Player
from Player.strategy import Strategy
from Player.first_s import FirstS
from Remote.remote_admin import RemoteAdmin
from Common.json_stream import StdinStdoutJSONStream
from TestHarnesses.xadmin import get_strategy_component
import sys

class Client():
    """
    Constructs a remote_admin with a player with a given strategy filepath and dynamically loads it. 
    It then connects the remote_admin to the server.
    """
    def __init__(self, ip: str, port: int, strategy: str):
        Strat = get_strategy_component(strategy)
        if Strat != None:
            self._remote_admin = RemoteAdmin(Player(Strat()))
            self._remote_admin.connect_to_admin(ip, port)
        
    def listen(self):   
       self._remote_admin.receive_messages()

def main():
    """
    Reads host and port from command line and strategy as a file path from stdin.
    Creates a Client using the given host, port, and strategy.
    """
    args = sys.argv

    host = 'LOCALHOST'
    port = 45678

    if len(args) > 1: host = args[1]
    if len(args) > 2: port = args[2]

    json_stream = StdinStdoutJSONStream()
    strategy_path = json_stream.receive_message().assert_value()
    
    try:
        c = Client(host, port, strategy_path)
    except Exception as e:
        return
    c.listen()

if __name__ == "__main__":
    main()
   