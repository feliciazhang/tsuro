# pylint: skip-file
from copy import deepcopy

from pyrsistent import pmap

from Common.board import Board
from Common.board_observer import BoardObserver, LoggingObserver
from Common.board_position import (
    MAX_BOARD_COORDINATE,
    MIN_BOARD_COORDINATE,
    BoardPosition,
)
from Common.board_state import BoardState
from Common.color import ColorString
from Common.moves import InitialMove, IntermediateMove
from Common.result import Result, error, ok
from Common.tiles import Port, index_to_tile, make_tiles


def test_board_initial_move() -> None:
    b = Board()

    logging_observer = LoggingObserver()
    b.add_observer(logging_observer)

    pos = BoardPosition(1, 1)
    r = b.initial_move(InitialMove(pos, make_tiles()[0], Port.BottomRight, "red"))
    assert r.is_error()
    assert (
        r.error()
        == f"cannot make an initial move at position {pos} since it is not on the edge"
    )

    pos = BoardPosition(3, 0)
    port = Port.TopLeft
    r = b.initial_move(InitialMove(pos, make_tiles()[0], port, "red"))
    assert r.is_error()
    assert (
        r.error()
        == f"cannot make an initial move at position {pos}, port {port} since it does not face the interior of the "
        f"board"
    )

    b.place_tile_at_index_with_scissors(make_tiles()[0], BoardPosition(2, 0))
    r = b.initial_move(
        InitialMove(BoardPosition(2, 0), make_tiles()[1], Port.BottomRight, "blue")
    )
    assert r.is_error()
    assert (
        r.error()
        == "cannot place tile at position BoardPosition(x=2, y=0) since there is already a tile at that position"
    )

    r = b.initial_move(
        InitialMove(BoardPosition(3, 0), make_tiles()[1], Port.BottomRight, "blue")
    )
    assert r.is_error()
    assert (
        r.error()
        == "cannot make an initial move at position BoardPosition(x=3, y=0) since the surrounding tiles are not all "
        "empty"
    )

    r = b.initial_move(
        InitialMove(BoardPosition(1, 0), make_tiles()[1], Port.BottomRight, "blue")
    )
    assert r.is_error()
    assert (
        r.error()
        == "cannot make an initial move at position BoardPosition(x=1, y=0) since the surrounding tiles are not all "
        "empty"
    )

    b._board_state = b._board_state.with_live_players(
        b._board_state.live_players.set("red", (BoardPosition(2, 0), Port.BottomRight))
    )
    r = b.initial_move(
        InitialMove(BoardPosition(5, 0), make_tiles()[1], Port.BottomRight, "red")
    )
    assert r.is_error()
    assert (
        r.error() == "cannot place player red since the player is already on the board"
    )

    r = b.initial_move(
        InitialMove(BoardPosition(5, 0), make_tiles()[2], Port.BottomRight, "blue")
    )
    assert r.is_ok()
    assert b._board_state.get_tile(BoardPosition(5, 0)) == make_tiles()[2]
    assert b._board_state.live_players["blue"] == (
        BoardPosition(5, 0),
        Port.BottomRight,
    )

    r = b.initial_move(
        InitialMove(BoardPosition(9, 2), make_tiles()[2], Port.TopLeft, "white")
    )
    assert r.is_ok()
    assert b._board_state.get_tile(BoardPosition(9, 2)) == make_tiles()[2]
    b._board_state = b._board_state.with_live_players(
        b._board_state.live_players.set("white", (BoardPosition(9, 2), Port.TopLeft))
    )

    r = b.initial_move(
        InitialMove(BoardPosition(9, 4), make_tiles()[2], Port.TopLeft, "green")
    )
    assert r.is_ok()
    assert b._board_state.get_tile(BoardPosition(9, 4)) == make_tiles()[2]
    assert b._board_state.live_players["green"] == (BoardPosition(9, 4), Port.TopLeft)

    assert logging_observer.all_messages() == []


def test_board_intermediate_move_single_player() -> None:
    b = Board()

    logging_observer = LoggingObserver()
    b.add_observer(logging_observer)

    # Can't place a tile if they haven't moved
    r = b.intermediate_move(IntermediateMove(make_tiles()[2], "green"))
    assert r.is_error()
    assert r.error() == "cannot place a tile for player green since they are not alive"

    # An initial move for green
    r = b.initial_move(
        InitialMove(BoardPosition(9, 4), index_to_tile(0), Port.TopLeft, "green")
    )
    assert r.is_ok()
    assert b._board_state.get_tile(BoardPosition(9, 4)) == index_to_tile(0)
    assert b._board_state.live_players["green"] == (BoardPosition(9, 4), Port.TopLeft)

    # Add another tile and they move
    r = b.intermediate_move(IntermediateMove(index_to_tile(1), "green"))
    assert r.is_ok()
    assert b._board_state.live_players["green"] == (
        BoardPosition(x=9, y=3),
        Port.TopRight,
    )

    # And place a tile that will draw them off the edge of the board
    assert logging_observer.all_messages() == []
    r = b.intermediate_move(IntermediateMove(index_to_tile(4), "green"))
    assert r.is_ok()
    assert "green" not in b._board_state.live_players
    assert logging_observer.all_messages() == ["exited_board: green"]


def test_board_intermediate_move() -> None:
    b = Board()

    logging_observer = LoggingObserver()
    b.add_observer(logging_observer)

    # An initial move for green
    r = b.initial_move(
        InitialMove(BoardPosition(0, 1), index_to_tile(0), Port.RightBottom, "green")
    )
    assert r.is_ok()
    assert b._board_state.get_tile(BoardPosition(0, 1)) == index_to_tile(0)

    # An initial move for red
    r = b.initial_move(
        InitialMove(BoardPosition(0, 3), index_to_tile(0), Port.RightBottom, "red")
    )
    assert r.is_ok()
    assert b._board_state.get_tile(BoardPosition(0, 3)) == index_to_tile(0)
    assert b._board_state.live_players["green"] == (
        BoardPosition(0, 1),
        Port.RightBottom,
    )
    assert b._board_state.live_players["red"] == (BoardPosition(0, 3), Port.RightBottom)

    # Add a tile for green
    r = b.intermediate_move(IntermediateMove(index_to_tile(4), "green"))
    assert r.is_ok()
    assert b._board_state.get_tile(BoardPosition(1, 1)) == index_to_tile(4)
    assert b._board_state.live_players["green"] == (
        BoardPosition(1, 1),
        Port.BottomLeft,
    )
    assert b._board_state.live_players["red"] == (BoardPosition(0, 3), Port.RightBottom)

    # Add another tile for green to get closer to red
    r = b.intermediate_move(IntermediateMove(index_to_tile(22).rotate(), "green"))
    assert r.is_ok()
    assert b._board_state.get_tile(BoardPosition(1, 2)) == index_to_tile(22)
    assert b._board_state.live_players["green"] == (
        BoardPosition(1, 2),
        Port.BottomLeft,
    )
    assert b._board_state.live_players["red"] == (BoardPosition(0, 3), Port.RightBottom)

    # And another tile that will cause green and red to both traverse over the same tile
    r = b.intermediate_move(IntermediateMove(index_to_tile(2), "green"))
    assert r.is_ok()
    assert b._board_state.get_tile(BoardPosition(1, 3)) == index_to_tile(2)
    assert b._board_state.live_players["green"] == (
        BoardPosition(1, 3),
        Port.BottomLeft,
    )
    assert b._board_state.live_players["red"] == (BoardPosition(1, 3), Port.RightBottom)

    assert logging_observer.all_messages() == []


def test_board_intermediate_move_remove_player_after_loop() -> None:
    b = Board()

    logging_observer = LoggingObserver()
    b.add_observer(logging_observer)

    # An initial move for green
    r = b.initial_move(
        InitialMove(BoardPosition(0, 1), index_to_tile(4), Port.RightBottom, "green")
    )
    assert r.is_ok()
    assert b._board_state.get_tile(BoardPosition(0, 1)) == index_to_tile(4)
    assert b.live_players["green"] == (BoardPosition(0, 1), Port.RightBottom)

    # More moves for green that would create a loop
    r = b.intermediate_move(IntermediateMove(index_to_tile(4), "green"))
    assert r.is_ok()
    assert b._board_state.get_tile(BoardPosition(1, 1)) == index_to_tile(4)
    assert b._board_state.live_players["green"] == (
        BoardPosition(1, 1),
        Port.BottomLeft,
    )

    r = b.intermediate_move(IntermediateMove(index_to_tile(4), "green"))
    assert r.is_ok()
    assert b._board_state.get_tile(BoardPosition(1, 2)) == index_to_tile(4)
    assert b._board_state.live_players["green"] == (BoardPosition(1, 2), Port.LeftTop)

    assert logging_observer.all_messages() == []

    # This tile placement will make a loop. Test that it is detected, the player is removed, and a message is broadcast
    # to all of the defined observers. According to assignment 6 the player should be removed but the tile
    # should not be on the board.
    r = b.intermediate_move(IntermediateMove(index_to_tile(4), "green"))
    assert r.is_ok()
    assert "green" not in b.live_players
    assert b._board_state.get_tile(BoardPosition(0, 2)) is None
    assert logging_observer.all_messages() == [
        "entered_loop: green",
        "exited_board: green",
    ]


def test_board_intermediate_move_loop_moves_no_one_else() -> None:
    # If player A places a tile that sends them into a loop and player B is next to the would be placed tile,
    # player B does not move
    b = Board()

    logging_observer = LoggingObserver()
    b.add_observer(logging_observer)

    # An initial move for green
    r = b.initial_move(
        InitialMove(BoardPosition(0, 1), index_to_tile(4), Port.RightBottom, "green")
    )
    assert r.is_ok()
    assert b._board_state.get_tile(BoardPosition(0, 1)) == index_to_tile(4)
    assert b.live_players["green"] == (BoardPosition(0, 1), Port.RightBottom)

    # More moves for green to setup what we need to make a loop
    r = b.intermediate_move(IntermediateMove(index_to_tile(4), "green"))
    assert r.is_ok()
    assert b._board_state.get_tile(BoardPosition(1, 1)) == index_to_tile(4)
    assert b._board_state.live_players["green"] == (
        BoardPosition(1, 1),
        Port.BottomLeft,
    )

    r = b.intermediate_move(IntermediateMove(index_to_tile(4), "green"))
    assert r.is_ok()
    assert b._board_state.get_tile(BoardPosition(1, 2)) == index_to_tile(4)
    assert b._board_state.live_players["green"] == (BoardPosition(1, 2), Port.LeftTop)

    # And set up white next to the where the would-be loop would be created
    assert b.place_tile_at_index_with_scissors(
        index_to_tile(4), BoardPosition(0, 3)
    ).is_ok()
    b._board_state = b._board_state.with_live_players(
        b._board_state.live_players.set("white", (BoardPosition(0, 3), Port.TopRight))
    )

    # This tile placement will make a loop. Test that it is detected, the player is removed, and a message is broadcast
    # to all of the defined observers. According to assignment 6 the player should be removed but the tile
    # should not be on the board.
    assert logging_observer.all_messages() == []
    r = b.intermediate_move(IntermediateMove(index_to_tile(4), "green"))
    assert r.is_ok()
    assert "green" not in b.live_players
    assert b._board_state.get_tile(BoardPosition(0, 2)) is None
    assert logging_observer.all_messages() == [
        "entered_loop: green",
        "exited_board: green",
    ]

    # And white is still in the same place
    assert b._board_state.live_players["white"] == (BoardPosition(0, 3), Port.TopRight)


def test_create_board_from_initial_placements() -> None:
    assert (
        Board.create_board_from_initial_placements([]).assert_value().get_board_state()
        == BoardState()
    )

    board_r = Board.create_board_from_initial_placements(
        [
            InitialMove(
                BoardPosition(5, 0), index_to_tile(2), Port.BottomRight, "blue"
            ),
            InitialMove(BoardPosition(9, 2), index_to_tile(3), Port.TopLeft, "white"),
            InitialMove(BoardPosition(9, 4), index_to_tile(4), Port.TopLeft, "green"),
        ]
    )
    assert board_r.is_ok()
    board_state = board_r.value().get_board_state()
    for x in range(MIN_BOARD_COORDINATE, MAX_BOARD_COORDINATE + 1):
        for y in range(MIN_BOARD_COORDINATE, MAX_BOARD_COORDINATE + 1):
            tile = board_state.get_tile(BoardPosition(x, y))
            if (x, y) == (5, 0):
                assert tile == index_to_tile(2)
            elif (x, y) == (9, 2):
                assert tile == index_to_tile(3)
            elif (x, y) == (9, 4):
                assert tile == index_to_tile(4)
            else:
                assert tile is None
    assert board_r.value().live_players == pmap(
        {
            "blue": (BoardPosition(x=5, y=0), 4),
            "green": (BoardPosition(x=9, y=4), 0),
            "white": (BoardPosition(x=9, y=2), 0),
        }
    )

    board_r = Board.create_board_from_initial_placements(
        [
            InitialMove(BoardPosition(5, 0), make_tiles()[2], Port.BottomRight, "blue"),
            InitialMove(BoardPosition(9, 2), make_tiles()[2], Port.TopLeft, "white"),
            InitialMove(BoardPosition(9, 4), make_tiles()[2], Port.TopLeft, "green"),
            # And an invalid one
            InitialMove(BoardPosition(9, 7), make_tiles()[2], Port.TopLeft, "green"),
        ]
    )
    assert board_r.is_error()
    assert (
        board_r.error()
        == "failed to create board from set of initial placements: cannot place player green since the player is already on the board"
    )


def test_create_board_from_moves() -> None:
    assert (
        Board.create_board_from_moves([], []).assert_value().get_board_state()
        == BoardState()
    )

    board_r = Board.create_board_from_moves(
        [
            InitialMove(
                BoardPosition(5, 0), index_to_tile(2), Port.BottomRight, "blue"
            ),
            InitialMove(BoardPosition(9, 2), index_to_tile(3), Port.TopLeft, "white"),
            InitialMove(BoardPosition(9, 4), index_to_tile(4), Port.TopLeft, "green"),
        ],
        [
            IntermediateMove(index_to_tile(5), "blue"),
            IntermediateMove(index_to_tile(6), "white"),
        ],
    )
    assert board_r.is_ok()
    board_state = board_r.value().get_board_state()
    for x in range(MIN_BOARD_COORDINATE, MAX_BOARD_COORDINATE + 1):
        for y in range(MIN_BOARD_COORDINATE, MAX_BOARD_COORDINATE + 1):
            if (x, y) == (5, 0):
                assert board_state.get_tile(BoardPosition(x, y)) == index_to_tile(2)
            elif (x, y) == (5, 1):
                assert board_state.get_tile(BoardPosition(x, y)) == index_to_tile(5)
            elif (x, y) == (9, 1):
                assert board_state.get_tile(BoardPosition(x, y)) == index_to_tile(6)
            elif (x, y) == (9, 2):
                assert board_state.get_tile(BoardPosition(x, y)) == index_to_tile(3)
            elif (x, y) == (9, 4):
                assert board_state.get_tile(BoardPosition(x, y)) == index_to_tile(4)
            else:
                assert board_state.get_tile(BoardPosition(x, y)) is None
    assert board_r.value().live_players == pmap(
        {
            "blue": (BoardPosition(x=5, y=1), 2),
            "green": (BoardPosition(x=9, y=4), 0),
            "white": (BoardPosition(x=9, y=1), 7),
        }
    )

    board_r = Board.create_board_from_moves(
        [
            InitialMove(
                BoardPosition(5, 0), index_to_tile(2), Port.BottomRight, "blue"
            ),
            InitialMove(BoardPosition(9, 2), index_to_tile(3), Port.TopLeft, "white"),
            InitialMove(BoardPosition(9, 4), index_to_tile(4), Port.TopLeft, "green"),
        ],
        [
            IntermediateMove(index_to_tile(5), "blue"),
            IntermediateMove(index_to_tile(6), "white"),
            # An invalid second move since black never had an initial move
            IntermediateMove(index_to_tile(7), "black"),
        ],
    )
    assert board_r.is_error()
    assert (
        board_r.error()
        == "failed to create board from moves: cannot place a tile for player black since they are not alive"
    )

    board_r = Board.create_board_from_moves(
        [
            InitialMove(
                BoardPosition(5, 0), index_to_tile(2), Port.BottomRight, "blue"
            ),
            InitialMove(BoardPosition(9, 2), index_to_tile(3), Port.TopLeft, "white"),
            InitialMove(BoardPosition(9, 4), index_to_tile(4), Port.TopLeft, "green"),
            # An invalid first move since someone placed a tile next to this position
            InitialMove(BoardPosition(9, 3), index_to_tile(7), Port.TopRight, "black"),
        ],
        [
            IntermediateMove(index_to_tile(5), "blue"),
            IntermediateMove(index_to_tile(6), "white"),
        ],
    )
    assert board_r.is_error()
    assert (
        board_r.error()
        == "failed to create board from set of initial placements: cannot make an initial move at position BoardPosition(x=9, y=3) since the surrounding tiles are not all empty"
    )


def test_board_surrounding_positions_are_empty() -> None:
    b = Board()

    assert b.place_tile_at_index_with_scissors(
        index_to_tile(1), BoardPosition(3, 2)
    ).is_ok()
    assert b._board_state.surrounding_positions_are_empty(BoardPosition(3, 2))
    assert not b._board_state.surrounding_positions_are_empty(BoardPosition(2, 2))
    assert not b._board_state.surrounding_positions_are_empty(BoardPosition(4, 2))
    assert not b._board_state.surrounding_positions_are_empty(BoardPosition(3, 1))
    assert not b._board_state.surrounding_positions_are_empty(BoardPosition(3, 3))


def test_board_port_faces_interior() -> None:
    b = Board()

    assert not b._board_state.port_faces_interior(BoardPosition(0, 5), Port.LeftTop)
    assert not b._board_state.port_faces_interior(BoardPosition(0, 5), Port.LeftBottom)
    assert b._board_state.port_faces_interior(BoardPosition(0, 5), Port.RightTop)

    assert not b._board_state.port_faces_interior(BoardPosition(5, 0), Port.TopLeft)
    assert not b._board_state.port_faces_interior(BoardPosition(5, 0), Port.TopRight)
    assert b._board_state.port_faces_interior(BoardPosition(5, 0), Port.LeftBottom)

    assert not b._board_state.port_faces_interior(BoardPosition(9, 5), Port.RightTop)
    assert not b._board_state.port_faces_interior(BoardPosition(9, 5), Port.RightBottom)
    assert b._board_state.port_faces_interior(BoardPosition(9, 5), Port.LeftTop)

    assert not b._board_state.port_faces_interior(BoardPosition(5, 9), Port.BottomRight)
    assert not b._board_state.port_faces_interior(BoardPosition(5, 9), Port.BottomLeft)
    assert b._board_state.port_faces_interior(BoardPosition(5, 9), Port.RightTop)


def test_board_move_player_along_path_error() -> None:
    b = Board()

    r = b._move_player_along_path("red")
    assert r.is_error()
    assert (
        r.error()
        == "failed to move player red along path: player red is not on the board"
    )


def test_board_to_html() -> None:
    # Just test that it returns a string and rely on manual testing to verify that it
    # looks roughly correct
    b = Board()
    assert isinstance(b.get_board_state().to_html(), str)

    board_r = Board.create_board_from_moves(
        [
            InitialMove(
                BoardPosition(5, 0), index_to_tile(2), Port.BottomRight, "blue"
            ),
            InitialMove(BoardPosition(9, 2), index_to_tile(3), Port.TopLeft, "white"),
            InitialMove(BoardPosition(9, 4), index_to_tile(4), Port.TopLeft, "green"),
        ],
        [
            IntermediateMove(index_to_tile(5), "blue"),
            IntermediateMove(index_to_tile(6), "white"),
        ],
    )
    assert board_r.is_ok()
    b2 = board_r.value().get_board_state()
    assert isinstance(b2.to_html(), str)
    assert b2.to_html() != b.get_board_state().to_html()
    assert b2.to_html(automatic_refresh=True) != b2.to_html(automatic_refresh=False)


def test_multi_collision() -> None:
    b = Board()

    logging_observer = LoggingObserver()
    b.add_observer(logging_observer)

    r = b.initial_move(
        InitialMove(BoardPosition(0, 0), index_to_tile(4), Port.BottomRight, "red")
    )
    assert r.is_ok()
    assert b._board_state.get_tile(BoardPosition(0, 0)) == index_to_tile(4)
    assert b.live_players["red"] == (BoardPosition(0, 0), Port.BottomRight)

    r = b.initial_move(
        InitialMove(BoardPosition(2, 0), index_to_tile(22), Port.LeftBottom, "green")
    )
    assert r.is_ok()
    assert b._board_state.get_tile(BoardPosition(2, 0)) == index_to_tile(22)
    assert b.live_players["green"] == (BoardPosition(2, 0), Port.LeftBottom)

    r = b.initial_move(
        InitialMove(BoardPosition(4, 0), index_to_tile(22), Port.LeftBottom, "blue")
    )
    assert r.is_ok()
    assert b._board_state.get_tile(BoardPosition(4, 0)) == index_to_tile(22)
    assert b.live_players["blue"] == (BoardPosition(4, 0), Port.LeftBottom)

    r = b.initial_move(
        InitialMove(BoardPosition(6, 0), index_to_tile(22), Port.LeftBottom, "white")
    )
    assert r.is_ok()
    assert b._board_state.get_tile(BoardPosition(6, 0)) == index_to_tile(22)
    assert b.live_players["white"] == (BoardPosition(6, 0), Port.LeftBottom)

    r = b.initial_move(
        InitialMove(BoardPosition(8, 0), index_to_tile(22), Port.LeftBottom, "black")
    )
    assert r.is_ok()
    assert b._board_state.get_tile(BoardPosition(8, 0)) == index_to_tile(22)
    assert b.live_players["black"] == (BoardPosition(8, 0), Port.LeftBottom)

    r = b.intermediate_move(IntermediateMove(index_to_tile(22), "black"))
    assert r.is_ok()
    assert b._board_state.get_tile(BoardPosition(7, 0)) == index_to_tile(22)

    r = b.intermediate_move(IntermediateMove(index_to_tile(22), "black"))
    assert r.is_ok()
    assert b._board_state.get_tile(BoardPosition(5, 0)) == index_to_tile(22)

    r = b.intermediate_move(IntermediateMove(index_to_tile(22), "black"))
    assert r.is_ok()
    assert b._board_state.get_tile(BoardPosition(3, 0)) == index_to_tile(22)

    r = b.intermediate_move(IntermediateMove(index_to_tile(22), "black"))
    assert r.is_ok()
    assert b._board_state.get_tile(BoardPosition(1, 0)) == index_to_tile(22)

    assert len(b._board_state.live_players) == 5
    assert len(set(b._board_state.live_players.values())) == 1
    assert b.live_players == pmap(
        {
            "black": (BoardPosition(x=0, y=0), 4),
            "blue": (BoardPosition(x=0, y=0), 4),
            "green": (BoardPosition(x=0, y=0), 4),
            "red": (BoardPosition(x=0, y=0), 4),
            "white": (BoardPosition(x=0, y=0), 4),
        }
    )


def test_board_place_tile_at_index_with_scissors() -> None:
    b = Board()
    assert b.place_tile_at_index_with_scissors(
        index_to_tile(5), BoardPosition(3, 0)
    ).is_ok()
    assert b.get_board_state().get_tile(BoardPosition(3, 0)) == index_to_tile(5)
    r = b.place_tile_at_index_with_scissors(index_to_tile(5), BoardPosition(3, 0))
    assert r.is_ok()
