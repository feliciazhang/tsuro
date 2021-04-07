# Board Specification

This document serves to further assist in the implementation of a Tsuro game by providing a strict 
internal data representation and interface for the board data that will be used by players and referees.  
The implementation of this specification must be written in Python 3.6.8, use type hints, and pass 
`mypy --strict && pylint` without any errors.

## Software Components

### Classes & Data

```python
class BoardPosition:
    # Represents a position on the board as x and y coordinates. x and y are zero-indexed coordinates
    # starting in the top left corner of the board (eg 0,0 means the top-left corner and 9,9 means the
    # bottom-right corner). x and y must be in the range 0 to 9 inclusive.
    x: int
    y: int

    def is_corner(self) -> bool:
        # Returns whether or not this BoardPosition is on the corner of a square board (with dimensions
        # MIN_BOARD_COORDINATE and MAX_BOARD_COORDINATE)

    def is_edge(self) -> bool:
        # Returns whether or not this BoardPosition is on the edge of a square board (with dimensions
        # MIN_BOARD_COORDINATE and MAX_BOARD_COORDINATE)

    def __deepcopy__(self):
        # Create a deep copy of itself. Abides by the standards set forth by Python 3's copy.deepcopy().

class BoardState:
    # BoardState is a view of the current board state. This class is meant to be shared with player
    # strategies and rule checkers. Prior to sharing, it should be deep copied in order to ensure that
    # malicious code cannot mutate the game data contained within. Board is the only class that is
    # allowed to modify the data internal to BoardState. All other classes must treat BoardState as an
    # immutable description of the state of a Tsuro board.

    # board is a list of lists of optional Tile, representing a list of rows on the board. Both the
    # outer list and the nested lists are all required to be of length 10, meaning that the board should
    # be initialized as a List[List[None]].
    board: List[List[Optional[Tile]]]

    # live_players is a list of the players (represented by color strings) that are still alive on this
    # board. Specified so that player strategies can determine which pieces are playing and so that the
    # referee can determine the winners based off of who was on the board on the previous tick.
    live_players: Mapping[ColorString, Tuple[BoardPosition, PortID]]

    def get_tile(self, pos: BoardPosition) -> Optional[Tile]:
        # Get the tile at the given position if it exists. Otherwise None.

    def get_position_of_player(self, player: ColorString) -> Result[Tuple[BoardPosition, PortID]]:
        # Get the position of the player specified by a color. Returns a result containing their
        # position on the board and the port they're on, or an error if they are not alive.

    def calculate_adjacent_position_of_player(
        self, player: ColorString
    ) -> Result[Optional[BoardPosition]]:
        # Calculate the Board Position adjacent to the tile and port that specified player is on. Return
        # a result with an error if the player is not alive.

    def __deepcopy__(self, memo: Any) -> "BoardState":
        # Create a deep copy of itself. Abides by the standards set forth by Python 3's copy.deepcopy().

class Board:
    # Board is a mutable definition of the Board that is used by the referee. Board works via modifying
    # the internal BoardState data to advance the game.

    _board_state: BoardState

    def add_observer(self, observer: BoardObserver) -> None:
        # Add the given board observer to this board. The board observer will then receive events
        # detailing the key actions that happened on this board. Makes sure to silence all exceptions
        # thrown by the observer.

    def get_board_state(self) -> BoardState:
        # Get a copy of the board state contained within this board.

    def validate_initial_move(self, move: InitialMove) -> Result[None]:
        # Validate the given initial move to ensure it adheres to a variety of physical constraints,
        # including that the player is living, the InitialMove has a position, the position is an edge,
        # the surrounding positions are open, and the port faces into the board.

    def initial_move(self, move: InitialMove) -> Result[None]:
        # Place the given initial move on this board. Should use self.validate_initial_move() in order
        # to validate the move. This operation should also be atomic, and should only save the board
        # state if all errors are handled. Returns a result with an error if the move is invalid, or
        # just a result with the value None if the move is valid.

    def initial_move_with_scissors(self, move: InitialMove) -> Result[None]:
        # Place an initial move without any validation (hence the with_scissors). This method is only
        # recommended to be used with extreme care and not exposed to any untrusted users. With the
        # exception of validation, this method is identical to self.initial_move(), including that it is
        # atomic.

    def validate_place_tile(self, move: IntermediateMove) -> Result[None]:
        # Validate the given tile placement move, ensuring that the player is still alive.

    def place_tile(self, move: IntermediateMove) -> Result[None]:
        # Place the given tile at the given position on this board. Should use
        # self.validate_place_tile() in order to validate this move, then attempt to place the adjacent
        # tile. After placing the tile, it tries to move all players to their new locations. This
        # operation should also be atomic, and should only save the board state if all errors are
        # handled. Returns a result with an error if the move is invalid, or just a result with the
        # value None if the move is valid.

    def place_tile_at_index_with_scissors(self, tile: Tile, pos: BoardPosition) -> Result[None]:
        # Place a tile at the specified index. with_scissors because this does minimal validation of the
        # tile placement and only verifies that it does not overwrite another tile. This operation
        # should also be atomic, and should only save th eboard state if all errors are handled. Returns
        # a result with an error if the move is invalid, or just a result with the value None if the
        # move is valid.

    @staticmethod
    def create_board_from_initial_placements(initial_placements: List[InitialMove]) -> Result["Board"]:
        # Create a board from the given list of initial placements. The list is ordered in the order
        # that the moves will be applied. Returns a result containing either the instantiated board
        # or an error.

    @staticmethod
    def create_board_from_moves(
        initial_placements: List[InitialMove], moves: List[IntermediateMove]
    ) -> Result["Board"]:
        # Create a board from the given list of initial placements and the given list of subsequent
        # moves. Both lists are ordered in the order that the moves will be applied. Returns a result
        # containing either the instantiated board or an error.

class Tile:
    # Represents an immutable Tsuro tile. Note that the tile itself does not store any data about which
    # players are on which ports.

    # _edges is a list of pairs of PortID, defining which ports are connected on the tile. The PortIDs
    # in each Tuple are required to be stored in ascending order, as are the tuples in the _edges list.
    # An edge represents an undirected edge. Each PortID must appear in the list of edges exactly once
    # and the list of edges must be of length 4.
    _edges: List[Tuple[PortID, PortID]]

    def rotate(self) -> "Tile":
        # Create a new tile that is equivalent to this one but rotated by 90 degrees clockwise.

    def all_rotations(self) -> "List[Tile]":
        # Get all of the possible rotations of tihs tile. Returns the rotations in the order 0 degrees
        # clockwise, 90 degrees clockwise, 180 degrees clockwise, and 270 degrees clockwise from the
        # current tile.

    def get_port_connected_to(self, port: PortID) -> PortID:
        # Get the ID of the port that is connected to the given port by an edge.

    def __deepcopy__(self, memo) -> "Tile":
        # Create a deep copy of itself. Abides by the standards set forth by Python 3's copy.deepcopy().

    def __hash__(self) -> int:
        # The Tile should be able to be hashed to a number that is not dependent on its orientation.
        # This means that `tile.__hash__() == tile.rotate().__hash__()`. This is useful for checking the
        # same tile for equality even if it is rotated.

    def __eq__(self, other: Any) -> bool:
        # Should use the same method as __hash__ uses in order to check equality with tiles that may
        # have been rotated.

# A new type to represent the valid PortIDs
PortID = NewType("PortID", int)

class Port:
    # A Port is represented as an enum of PortIDs. A square Tile has 8 ports total, 2 per side.

    # `TopLeft` means the left port on the top side. `LeftTop` means the top port on the left side.
    TopLeft = PortID(0)
    TopRight = PortID(1)
    RightTop = PortID(2)
    RightBottom = PortID(3)
    BottomRight = PortID(4)
    BottomLeft = PortID(5)
    LeftBottom = PortID(6)
    LeftTop = PortID(7)

The PortID numbers are assigned following this diagram:

+-----0------1------+
|                   |
7                   2
|                   |
|                   |
6                   3
|                   |
|                   |
+-----5------4------+

# A color string represents the colored token belonging to a specific player.
ColorString = Literal["white", "black", "red", "green", "blue"]
```
