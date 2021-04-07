# Tsuro Sequence Diagrams

The start up flow and processing phase of the Tsuro software system are depicted below for two players. Note that it could be scaled to N players but is shown for two players for simplicity purposes. 

### Start Up Steps:

```
                +-----------------+           +-----------+           +-----------------+
                | Player2Strategy |           | Game_Loop |           | Player1Strategy |
                +-----------------+           +-----------+           +-----------------+
                         |                          |                          |
                         |                          | set_color: ColorString   |
                         |                          |------------------------->|
                         |                          |                          |
                         |   set_color: ColorString |                          |
                         |<-------------------------|                          |
                         |                          | generate_first_move:     |
                         |                          | List[Tile], BoardState   |
                         |                          |------------------------->| -----------------------\
                         |                          |                          | | Chooses a tile from  |
                         |                          |                          |-| the list of tiles to |
                         |                          |                          | | place on the board   |
                         |                          |                          | |----------------------|
                         |                          |               Move, Port |
                         |                          |--------------------------|
                         |   generate_first_move:   |                          |
                         |   List[Tile], BoardState |                          |
-----------------------\ |<-------------------------|                          |
| Chooses a tile from  | |                          |                          |
| the list of tiles to |-|                          |                          |
| place on the board   | |                          |                          |
|----------------------| |                          |                          |
                         | Move, Port               |                          |
                         |------------------------->|                          |
                         |                          |                          |
```

Note that if a player strategy returns an invalid move, the move will be discarded and the player strategy does not get a chance to retry. 

### Steady State

```
                                                       +-----------------+                              +-----------+                                                +-----------------+
                                                       | Player2Strategy |                              | Game_Loop |                                                | Player1Strategy |
                                                       +-----------------+                              +-----------+                                                +-----------------+
                                                                |                                             | -------------------------------------\                        |
                                                                |                                             |-| If Player 1 is still on the board: |                        |
                                                                |                                             | |------------------------------------|                        |
                                                                |                                             |                                                               |
                                                                |                                             | generate_move: List[Tile], BoardState                         |
                                                                |                                             |-------------------------------------------------------------->|
                                                                |                                             |                                                               | --------------------------------------------------------------\
                                                                |                                             |                                                               |-| Chooses a tile from the list of tiles to place on the board |
                                                                |                                             |                                                               | |-------------------------------------------------------------|
                                                                |                                             |                                                               |
                                                                |                                             |                                                          Move |
                                                                |                                             |<--------------------------------------------------------------|
                                                                |      -------------------------------------\ |                                                               |
                                                                |      | If Player 2 is still on the board: |-|                                                               |
                                                                |      |------------------------------------| |                                                               |
                                                                |                                             |                                                               |
                                                                |       generate_move: List[Tile], BoardState |                                                               |
                                                                |<--------------------------------------------|                                                               |
--------------------------------------------------------------\ |                                             |                                                               |
| Chooses a tile from the list of tiles to place on the board |-|                                             |                                                               |
|-------------------------------------------------------------| |                                             |                                                               |
                                                                |                                             |                                                               |
                                                                | Move                                        |                                                               |
                                                                |-------------------------------------------->|                                                               |
                                                                |                                             | ----------------------------------------------------- \       |
                                                                |                                             |-| If only one player is left on the board, terminate. |       |
                                                                |                                             | | Otherwise, loop.                                    |       |
                                                                |                                             | |---------------------------------------------------- |       |
                                                                |                                             |                                                               |

```

Note that if a player strategy returns an invalid move, the move will be discarded and the player strategy does not get a chance to retry. 

### Shutdown Phase

The program will shut down when one of three conditions is met:

* There is only one avatar left that has not reached the board's periphery. This avatar's owner is the winner. 
* Two or more avatars reach the board's periphery during the same round. The owners of these avatars are joint winners. 
* All avatars remaining on the board are in a closed loop whereby it is impossible for them to ever reach the end of the board. The owners of these avatars are joint winners. 

When the program shuts down, the `start_game_loop` function returns a list of the winners which will be printed to stdout. 