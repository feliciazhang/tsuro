"""
    Test harness for assignment 10.
"""

from Common.json_stream import StdinStdoutJSONStream
from Remote.client import Client
from TestHarnesses.xadmin import get_strategy_component
from Common.tsuro_types import JSON
from typing import List, Tuple, Set
import sys
from threading import Thread
from Common.util import timeout

TIMEOUT_SECONDS = 60

def main() -> None:
    args = sys.argv
    host = 'LOCALHOST'
    port = 45678

    if len(args) > 1: host = args[1]
    if len(args) > 2: port = int(args[2])

    json_stream = StdinStdoutJSONStream()
    player_info = json_stream.receive_message().assert_value()
   
    create_clients(player_info, host, port)

def create_clients(player_info: JSON, host: str, port: int)-> List[Tuple]:
    """
    Create a client for every spec in the given player info. 
    """
    all_clients = []
    threads = []
   
    for spec in player_info:
        # checks if any players have the same name
        if not any(spec["name"] == client[0] for client in all_clients):
            try:
                c = Client(host, port, spec["strategy"])
            except:
                continue
            thread = Thread(target=c.listen)
            thread.start()
            threads.append(thread)
            all_clients.append((spec["name"], c))
    
    for thread in threads:
        thread.join()
   

if __name__ == "__main__":
    main()