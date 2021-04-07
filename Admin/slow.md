# Slow

Commit ID: [77ee2e73346584aafcadf08da3c7c4e5543fd60d](https://github.ccs.neu.edu/cs4500-fall2019/JS/commit/77ee2e73346584aafcadf08da3c7c4e5543fd60d)  
Message: Added functionality to handle player timeouts

## Implementation

Our precedecessors implemented a [timeout decorator](../Common/util.py) that raises an exception if some logic takes more than a given amount of time to run. We used this in the Referee and Administrator whenever a function on a player was called with a timeout of 3 seconds. Since there were multiple player calls in Referee, we created a helper called `_handle_player_timeout` which took in the player's color and the function on the player, called the function and returned the value. If the timeout was exeeded or an exception was raised, the function catches the exception and sets the given player as a cheating player. Because there is only one function call on players in Administrator, we did not create a helper, but the logic acts similarly.
