"""
A module holding the Tsuro color definitions
"""
from typing import List

from typing_extensions import Literal

# A color string represents the colored token belonging to a specific player.
ColorString = Literal["white", "black", "red", "green", "blue"]

# A list of all the possible colors. This order matches the order defined in Tsuro Tile Types by Matthias
AllColors: List[ColorString] = ["white", "black", "red", "green", "blue"]
