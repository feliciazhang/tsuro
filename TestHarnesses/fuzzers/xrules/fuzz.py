"""
A simply python script meant to fuzz xrules via generating board states followed by a single move.
"""
# pylint: skip-file
import random
from typing import List

from Common.board_position import MAX_BOARD_COORDINATE, MIN_BOARD_COORDINATE
from Common.color import AllColors
from Common.json_stream import json_dump
from Common.tiles import Port, port_id_to_network_port_id
from Common.tsuro_types import JSON
from Common.util import get_tsuro_root_path


def random_tile_pat() -> JSON:
    return [random.randint(0, 34), random.choice([0, 90, 180, 270])]


def generate_testcase() -> List[JSON]:
    num_players = random.randint(3, 5)
    players = random.sample(AllColors, k=num_players)
    num_tiles = random.randint(0, 90)
    possible_positions = set()
    for x in range(MIN_BOARD_COORDINATE, MAX_BOARD_COORDINATE + 1):
        for y in range(MIN_BOARD_COORDINATE, MAX_BOARD_COORDINATE + 1):
            possible_positions.add((x, y))

    board_state = []
    for i in range(num_tiles):
        x, y = random.choice(list(possible_positions))
        possible_positions.remove((x, y))
        board_state.append([random_tile_pat(), x, y])

    for player in players:
        while True:
            if len(possible_positions) == 0:
                return generate_testcase()
            x, y = random.choice(list(possible_positions))
            possible_positions.remove((x, y))
            for port in Port.all():
                if port in [Port.TopLeft, Port.TopRight]:
                    if y - 1 >= 0:
                        if (x, y - 1) in possible_positions:
                            break
                elif port in [Port.RightTop, Port.RightBottom]:
                    if x + 1 <= MAX_BOARD_COORDINATE:
                        if (x + 1, y) in possible_positions:
                            break
                elif port in [Port.BottomLeft, Port.BottomRight]:
                    if y + 1 <= MAX_BOARD_COORDINATE:
                        if (x, y + 1) in possible_positions:
                            break
                elif port in [Port.LeftBottom, Port.LeftTop]:
                    if x - 1 >= MIN_BOARD_COORDINATE:
                        if (x - 1, y) in possible_positions:
                            break
            else:
                continue
            board_state.append(
                [random_tile_pat(), player, port_id_to_network_port_id(port), x, y]
            )
            break
    tile_pat = random_tile_pat()
    random_move = [
        [random.choice(players), tile_pat],
        tile_pat[0],
        random.randint(0, 34),
    ]
    return [board_state, random_move]


if __name__ == "__main__":
    tc = generate_testcase()
    print(json_dump(tc[0]))
    print(json_dump(tc[1]))
