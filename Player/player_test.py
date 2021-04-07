# pylint: skip-file
from Common.board_position import BoardPosition
from Common.board_state import BoardState
from Common.moves import InitialMove, IntermediateMove
from Common.tiles import Port, index_to_tile
from Player.first_s import FirstS
from Player.player import Player
from Player.player_observer import LoggingPlayerObserver
from Player.strategy import Strategy


def test_player_calls_observers() -> None:
    bs = BoardState()

    lo = LoggingPlayerObserver()
    p = Player(FirstS())
    p.add_observer(lo)

    p.set_color("red")
    assert lo.set_colors == ["red"]
    p.set_color("green")
    assert lo.set_colors == ["red", "green"]

    assert p.generate_first_move(
        [index_to_tile(3), index_to_tile(4), index_to_tile(5)], bs
    ).is_ok()
    assert lo.initial_move_offereds == [
        ([index_to_tile(3), index_to_tile(4), index_to_tile(5)], bs)
    ]
    assert lo.initial_move_playeds == [
        (
            [index_to_tile(3), index_to_tile(4), index_to_tile(5)],
            bs,
            InitialMove(BoardPosition(1, 0), index_to_tile(5), Port.RightTop, "green"),
        )
    ]

    assert p.generate_move([index_to_tile(10), index_to_tile(11)], bs).is_ok()
    assert lo.intermediate_move_offereds == [
        ([index_to_tile(10), index_to_tile(11)], bs)
    ]
    assert lo.intermediate_move_playeds == [
        (
            [index_to_tile(10), index_to_tile(11)],
            bs,
            IntermediateMove(index_to_tile(10), "green"),
        )
    ]

    gr = ([{"red"}, {"black", "green"}], {"white"})
    p.game_result(gr)  # type: ignore
    assert lo.game_results == [gr]


def test_player_failed_strategy() -> None:
    bs = BoardState()
    p = Player(Strategy())

    r = p.generate_move([], bs)
    assert r.error() == "Strategy does not implement method generate_move!"

    r2 = p.generate_first_move([], bs)
    assert r2.error() == "Strategy does not implement method generate_first_move!"
