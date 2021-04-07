## Changes made

Commit: [8ecf4d99f4f75e6528d0ed0dab9cc78449d6c626](https://github.ccs.neu.edu/cs4500-fall2019/JS/commit/8ecf4d99f4f75e6528d0ed0dab9cc78449d6c626)  
Message: default rulechecker and fix other_players  
Purpose: give players a default rulechecker and pass the correct list of other player colors to "others" message instead of all players

Commit: [875dca18bdf6eb213e7934165efdde019861bed2](https://github.ccs.neu.edu/cs4500-fall2019/JS/commit/875dca18bdf6eb213e7934165efdde019861bed2)  
Message: notify all players and board to state-pats  
Purpose: Fix admin to notify all players of tournament results, not just winners. Add helpers for turning a board state to state-pats  

Commit: [d0a7eae618254cb58e2440706f4bddf138d68e2b](https://github.ccs.neu.edu/cs4500-fall2019/JS/commit/d0a7eae618254cb58e2440706f4bddf138d68e2b)  
Message: added xserver and tested running tournaments with xclients  
Purpose: removed code that notifies cheaters of the tournament results 

Commit: [5da26b42fd48e7af2d13c9b4e14630e1ff5f140f](https://github.ccs.neu.edu/cs4500-fall2019/JS/commit/5da26b42fd48e7af2d13c9b4e14630e1ff5f140f)  
        [a837dc8213a42590aec73d5e88501b9c80cc1967](https://github.ccs.neu.edu/cs4500-fall2019/JS/commit/a837dc8213a42590aec73d5e88501b9c80cc1967)  
Message: fixing bug in rules for loops and suicides  
Purpose: fixed bug so that cases where all options result in a combination of
loops and suicides results in the player being a cheater  

## Client-server startup

                        user launches ./xserver
                                                                                      user launches ./xclients
                              Server                                                  Client     ...
                                +                     ++         RemoteAdmin             +
                  creates       |                     ||               +     creates     |       creates a RemoteAdmin
                  Administrator |                     || tcp connect   +<----------------+       with a Player
                                |                     ||  on init      |                 |
                                +<-------------------------------------+                 |
                                |                     ||               |                 |
                                |     RemotePlayer    ||               |                 |
                                |          +          ||               |                 |
                                | creates  |          ||               |                 |
                                +--------->+          ||               |                 |
                                |          |          ||               |                 |
            waits 60 seconds +--+          |          ||               |                 |
            or 20 clients    |  |          |          ||               |                 |
                             +->+          |          ||               |                 |
                                |          |          ||               |                 |
            house players +---->+          |          ||               |                 |
                                |          |          ||               |                 |
            runs tournament     |          |          ||               |                 |
            per remote.md       |          |          ||               |                 |
                                |          |          ||               |                 |
                                +          +          ++               +                 +
                                .          .          ..               .                 .

House players are signed up after remote players register. A second input is
read in xserver from stdin in the same format as remote players.
