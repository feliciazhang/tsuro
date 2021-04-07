# Rule Checker Specification

This document serves to further assist in the implementation of a Tsuro game by providing an interface 
for Tsuro rule checkers that will be used by players and referees. The implementation of this 
specification must be written in Python 3.6.8, use type hints, and pass `mypy --strict && pylint` 
without any errors.

## Software Components

A Tsuro rule checker will be a class that adheres to the below interface:

```python
# Using BoardPosition, BoardState, ColorString, PortID, and Tile from board.md.
# Using a Result type for return data (see `Tsuro/Common/result.py`) modeled after the result types in
#   Rust, Swift, etc

class RuleChecker:
    def validate_initial_move(
        self, board: BoardState, player: ColorString, pos: BoardPosition, tile: Tile, port: PortID, tile_choices: List[Tile]
    ) -> Result[None]:
        # Validate an initial move against the given board state. Also validates that the placed tile
        # is one of the tiles that the player was allowed to choose from. The initial move is being placed by
        # the player (represented by a color string) and consists of placing the given tile at the
        # specified board position with their token on the specified port ID. Returns a Result[None]
        # which contains either no error (meaning the move is valid) or an error containing an error
        # message.

    def validate_move(
        self, board: BoardState, player: ColorString, pos: BoardPosition, tile: Tile, tile_choices: List[Tile]
    ) -> Result[None]:
        # Validate a non-initial move against the given board state. Also validates that the placed tile
        # is one of the tiles that the player was allowed to choose from. The move is being placed by the
        # player (represented by a color string) and consists of placing the given tile at the specified
        # board position. Returns a Result[None] which contains either no error (meaning the move is
        # valid) or an error containing an error message.

    def can_player_move(self, player: ColorString) -> bool:
        # Return whether or not the given player (represented by a color string) is allowed to move.
        # This method is meant to support taking punitive actions against players. For example, this
        # method would make it possible to ban cheaters or force cheaters to skip a turn.

    def tick(self, board: BoardState, round_number: int, player: ColorString) -> None:
        # Called after each move is completed to allow the rule checker to keep track of successive
        # board states to determine the order of players on the leaderboard. The round number is an
        # incrementing integer that is incremented after each round of players played (eg after every
        # color string has placed a move) and player is the player who placed the most recent move.

    def is_game_over(self, board: BoardState) -> bool:
        # Returns whether or not the game is over

    def get_leaderboard() -> Result[Tuple[List[Set[ColorString]], Set[ColorString]]]:
        # Returns the leaderboard for a completed game. The first item in the tuple is a list of set of
        # color string, with the first item representing the set of players that got first place, the
        # second item representing the players that got second place, etc. The second item in the tuple
        # is the set of players who cheated at some point in the game. Returns an error if the game is
        # not yet over.
```