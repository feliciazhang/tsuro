from Common.json_stream import StdinStdoutJSONStream
from Remote.server import Server
import sys

"""
Takes in a port from the commandl line and player info from stdin in the same format as xclients, and constructs a Server. 
"""

def main():
    args = sys.argv
    port = 45678
    if len(args) > 1: port = args[1]

    json_stream = StdinStdoutJSONStream()
    player_info = json_stream.receive_message().assert_value()
    names = [player["name"] for player in list(player_info)]
    Server(port, names)

if __name__ == "__main__":
    main()