# Welcome

## Finding components

There were two README's present in the repository. One in /Planning and another
at the root directory which made it difficult to decide which one was the source of truth. Because the one in the root directory was more complete, we based our assumptions off of that README.

The README included multiple navigation diagrams which linked components that
are statically dependent on eachother. The second diagram shows that the
referee depends on the board and rules, which is represented by an arrow
pointing from the referee to each of those components. Likewise, rules has an
arrow pointing to board, indicating that it is statically dependent on the board.

[This section](./README.md#dynamic-dependencies-and-core-components) discusses
in words what each component represents. The section again explains which
components are related but does not explain how their used in conjunction
with one another. We had to investigate the code to determine which pieces
were dynamically dependent on one another.

## Investigating changes for collisions

The current codebase does not detect collisions among avatars. There exists
one test that verifies that collisions are allowed. In order to implement this 
change to their program, some code must be added to their [rule checker](../Common/rules.py) and [the referee](../Admin/referee.py).

We would add a new function called `causes_collision()` to the Gameboard that takes in a move and whether it would cause a collision. Then in the RuleChecker, we would add `move_causes_collision` that takes in a `board_state` and `IntermediateMove` and uses the Board's `causes_collision()`to return a `Result[bool]` which would be `True` if the resulting board state has any players on the same location and port. We would add logic that would call this new function at line 112 in `rules.py`. The function would return an error Result if the move does cause a collision.

The Referee has a function called `run_game_single_round` which uses the rule
checker to validate the player's tile choice. At line 267, the rule checker returns
an error Result, indicating that the player has cheated (which could have been
caused by a collision). In the current code, the tile does not get placed if any
type of cheating occurs. We would have to change this to check whether the error was
caused by a collision, and if so, place the tile anyway. We would also change
the error message that the Rule Checker creates so they'd be more easily
checkable to detect the cause of the error.

Throughout the codebase, each function has comments that generally explain the
purpose but are not explicit in discussing the task that it accomplishes. For
example, in `validate_move` in the rule checker, the purpose statement stays
that the function will validate a given move, however it does not explain
what a valid move is and in what situations the function should be used.
