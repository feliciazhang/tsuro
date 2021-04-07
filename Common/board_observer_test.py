# pylint: skip-file
from Common.board_observer import BoardObserver, LoggingObserver
from Common.color import ColorString
from Common.result import Result
from Common.util import silenced_object


def test_logging_observer() -> None:
    lo = LoggingObserver()
    assert lo.entered_loop == []
    assert lo.exited_board == []
    lo.player_entered_loop("red")
    assert lo.entered_loop == ["red"]
    assert lo.exited_board == []
    lo.player_entered_loop("green")
    assert lo.entered_loop == ["red", "green"]
    assert lo.exited_board == []
    lo.player_entered_loop("red")
    assert lo.entered_loop == ["red", "green", "red"]
    assert lo.exited_board == []

    lo.player_exited_board("white")
    assert lo.entered_loop == ["red", "green", "red"]
    assert lo.exited_board == ["white"]
    lo.player_exited_board("black")
    assert lo.entered_loop == ["red", "green", "red"]
    assert lo.exited_board == ["white", "black"]

    assert lo.all_messages() == [
        "entered_loop: red",
        "entered_loop: green",
        "entered_loop: red",
        "exited_board: white",
        "exited_board: black",
    ]


class CrashingBoardObserver(BoardObserver):
    def player_exited_board(self, player: ColorString) -> None:
        raise Exception("crashy boi")

    def player_entered_loop(self, player: ColorString) -> None:
        raise Exception("crashy boi")


def test_silent_board_observer() -> None:
    sbo = silenced_object(CrashingBoardObserver())

    sbo.player_exited_board("red")
    sbo.player_entered_loop("red")

    assert True
