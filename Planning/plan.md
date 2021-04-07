# Tsuro Project Analysis

This document is a project analysis and specification on implementing a software system for the game [Tsuro](http://www.ccs.neu.edu/home/matthias/4500-f19/tsuro.html) in Python 3.6.8. The goal of this software system is to run automated games and tournaments between different autonomous Tsuro players. The implementation of this specification must pass use type hints and `mypy --strict && pylint` without any errors. 

## Software Components

### Functions

```
def start_game_loop(players: Dict[ColorString, Tuple[int, PlayerStrategy]]) -> List[ColorString]:
    # Start the main game loop with the given playerstrategies represented by the given colors. Returns a list of
    # the winners of the game. This list may contain one or more winners. The int is the age of the player and players go in order of age
```

### Classes & Data

```python
class PlayerStrategy:
    def set_color(self, color: ColorString) -> None:
        # Set the color of this PlayerStrategy
    def generate_first_move(self, tiles: List[Tile], board_state: BoardState) -> Tuple[Move, Port]:
        # Generate the first move by choosing from the given list of tiles. Returns the move along with the port 
        # that the player's token should be placed on
    def generate_move(self, tiles: List[Tile], board_state: BoardState) -> Move:
        # Generate a move by choosing from the given list of tiles and return the move. 

class BoardState:
    def get_tile(self, x: int, y: int) -> Optional[Tile]:
        # Get the tile at the given x,y coordinate if it exists. Otherwise None. 
    def get_position_of_player(self, player: ColorString) -> Tuple[int, int, Port, bool]:
        # Get the position of the player specified by a color. Returns the x,y position, the port they are on, and False. If the player 
        # is in a loop, returns the x,y,port of where they started and True. 

class Tile:
    def get_port_connected_to(self, port: Port) -> Port:
        # Get the port that the given port is connected to on this tile
    def rotate(self, degrees: Literal[90, 180, 270]) -> Tile:
        # Rotate this tile by 90, 180, or 270 degrees clockwise to form a new but equivalent tile

# A Port is represented as an enum. `TopLeft` means the left part of the top side. `LeftTop` means the top part of 
# the left side. 
Port = Enum("Port", ("TopLeft", "TopRight", "RightTop", "RightBottom", "BottomRight", "BottomLeft", "LeftTop", "LeftBottom"))

# A Move is represented as a tuple of the x,y coordinates to place the tile on and the tile to be placed
Move = Tuple[int, int, Tile]

class Board:
    def get_board_state(self) -> BoardState:
        # Get an immutable copy of the board state inside this board
    def make_move(self, move: Move, tile_choice: List[Tile]) -> None:
        # Apply the specified move to this board. Verify that the tile specified in the move is one of the allowed 
        # tile choices. 
    def make_first_move(self, move: Move, tile_choice: List[Tile], port: Port, player: ColorString) -> None:
        # Make an initial move by applying the specified move to this board. Verify that the tile specified in the 
        # move is one of the allowed tile choices. Place the specified player token onto the specified port.
    def is_player_on_board(self, player: ColorString) -> bool:
        # Returns whether or not the player represented by the given color is still on the board
    def get_winner(self) -> Optional[ColorString]:
        # Returns the winner of this game of Tsuro if the game is over. Returns None otherwise. 
        
# A color string represents the color of a token that represents a player
ColorString = Literal["white", "black", "red", "green", "blue"]
```

## Implementation Plan

In order to implement the above software system for the Tsuro game, we will proceed in four phases.

### Phase 1: Interface Creation

We will start by defining all of the above classes, methods, and functions with the above type signatures. The bodies of the methods and functions will be left unimplemented. The types of the fields inside of the classes will be defined and purpose statements will be written. This will allow us to further refine the above specification in order to ensure it provides all of the capabilities that we need. In this phase, we will focus on the structure of our data as we further consider the problem. We expect that during this phase we may tweak some of the data definitions listed above.

### Phase 2: Game Loop Implementation

We will then define all of the code needed to run the main game loop except for the `PlayerStrategy` class. As we write the code, we will also write unit tests for individual functions. All of the functions in the above specification are designed to be easy to test in isolation. This will allow us to confirm that the main game loop is functional and properly implemented.

### Phase 3: Player Strategy Implementation

For the purpose of demoing this software, we will then proceed to implement a naive `PlayerStrategy` class that simply makes random moves. This is not meant to be a functional strategy but is simply meant for demoing the software with multiple automated players playing Tsuro against each other. In order to demo this software for any potential clients, we will also create a basic GUI during phase 3 that will make it possible to watch Tsuro games as they are played. This will include writing a basic entry point for the program that allows a user to specify the name of different classes that adhere to the PlayerStrategy interface that will be used when running the game. A user of the tsuro program will run it via `./tsuro --strategy StrategyClassNameOne --strategy StrategyClassNameTwo ...`.

In addition to demoing the software, this phase will also make it possible to write integration tests that exercise the entirety of the software system.

### Phase 4: Extensions

After completing the first three phases, it will be possible to run games of Tsuro with local autonomous players. One possible extension that our system is designed for is adding the ability to support network-connected autonomous players. Since all of the methods on the `PlayerStrategy` class return data (rather than mutating data), it would be very easy to define a protocol for network-connected autonomous players that sends the function arguments and returns values over the network. A variety of other possible extensions are possible given this design.