# Distributed system protocol
Tsuro can be made into a distributed system using the remote proxy pattern.

## Components

**Server side**  
The server has the Administrator, which creates and communicates with Referees. This is created by an overarching program (like a test harness) which also handles receiving TCP connections and creating `RemotePlayer`s. A `RemotePlayer` is extends the abstract class [`PlayerInterface`](../Common/player_interface.py) and represents a player on the client side. It is responsible for creating and sending and receiving TCP messages with a `RemoteAdmin` on the client side.

**Client side**  
A `Player` is created by an overarching program (like a test harness) with a corresponding `RemoteAdmin`. The `RemoteAdmin` handles connecting to Tsuro's server and communication via TCP with a `RemotePlayer`. It also translates messages for the `Player`.

![](./remote_diagram.png)

## Messaging

The sequence and usage of these messages are described below:

1. `["playing-as", [ColorString]]`  
Where the ColorString is a string representing the color of the avatar that the player is playing as in the game.  
Sent from each `RemotePlayer` to the corresponding `RemoteAdmin` to inform the player what color they are.

Response: `"void"`

2. `["others", [ColorString, ...]]`  
Where the payload is a list of ColorStrings representing the colors of the avatars of the other players in the game.  
Sent from each `RemotePlayer` to the corresponding `RemoteAdmin` to inform the player of the other players in the game.

Response: `"void"`

3. `["inital", initial]`  
Where `initial` is as described in the [assignment](http://www.ccs.neu.edu/~matthias/4500-f19/10.html#%28tech._initial%29).

Response: `action`    
Where `action` is as described in the assignment.

  
4. `["take-turn", intermediate]`  
Where `intermediate` is as described in the assignment.

Response: `tile-pat`  
Where `tile-pat` is a [tile-pat](https://felleisen.org/matthias/4500-f19/tiles.html#%28tech._tile._pat%29) representing the tile and rotation chosen.  
Sent from a `RemoteAdmin` to the corresponding `RemotePlayer` to indicate what move has been chosen by the player.

5. `["end-of-tournament", [Boolean]]`
Where the boolean represents whether the player won the tournament.  
Sent from a `RemotePlayer` to the corresponding `RemoteAdmin` to inform the player about their tournament result.

Response: `"void"`  
