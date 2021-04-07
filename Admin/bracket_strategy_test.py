# pylint: skip-file
from typing import Set, Tuple

from Admin.administrator import PlayerAge, PlayerID, TournamentResult
from Admin.bracket_strategy import SimpleBracketStrategy, flatten_leaderboards
from Common.util import flatten


def make_players(n: int) -> Set[Tuple[PlayerID, PlayerAge]]:
    ret = set()
    for i in range(n):
        ret.add((PlayerID(str(i)), PlayerAge(i)))
    return ret


def test_bucket_players_manual() -> None:
    bs = SimpleBracketStrategy()

    for i in range(0, 3):
        r = bs.bucket_players(make_players(i))
        assert r.is_error()
        assert (
            r.error()
            == "cannot create a Tsuro tournament with less than 3 players (tried %s)"
            % i
        )

    assert bs.bucket_players(make_players(6)).assert_value() == {
        frozenset({PlayerID("0"), PlayerID("1"), PlayerID("2")}),
        frozenset({PlayerID("3"), PlayerID("4"), PlayerID("5")}),
    }
    assert bs.bucket_players(make_players(7)).assert_value() == {
        frozenset({PlayerID("0"), PlayerID("1"), PlayerID("2"), PlayerID("3")}),
        frozenset({PlayerID("4"), PlayerID("5"), PlayerID("6")}),
    }
    assert bs.bucket_players(make_players(8)).assert_value() == {
        frozenset(
            {PlayerID("0"), PlayerID("1"), PlayerID("2"), PlayerID("3"), PlayerID("4")}
        ),
        frozenset({PlayerID("5"), PlayerID("6"), PlayerID("7")}),
    }
    assert bs.bucket_players(make_players(9)).assert_value() == {
        frozenset(
            {PlayerID("0"), PlayerID("1"), PlayerID("2"), PlayerID("3"), PlayerID("4")}
        ),
        frozenset({PlayerID("5"), PlayerID("6"), PlayerID("7"), PlayerID("8")}),
    }
    assert bs.bucket_players(make_players(10)).assert_value() == {
        frozenset(
            {PlayerID("0"), PlayerID("1"), PlayerID("2"), PlayerID("3"), PlayerID("4")}
        ),
        frozenset(
            {PlayerID("5"), PlayerID("6"), PlayerID("7"), PlayerID("8"), PlayerID("9")}
        ),
    }
    assert bs.bucket_players(make_players(11)).assert_value() == {
        frozenset(
            {PlayerID("0"), PlayerID("1"), PlayerID("2"), PlayerID("3"), PlayerID("4")}
        ),
        frozenset({PlayerID("5"), PlayerID("6"), PlayerID("7")}),
        frozenset({PlayerID("8"), PlayerID("9"), PlayerID("10")}),
    }


def test_bucket_players_properties() -> None:
    bs = SimpleBracketStrategy()

    for i in range(3, 100):
        r = bs.bucket_players(make_players(i))
        assert r.is_ok()
        sets = r.value()
        for elem in sets:
            assert 3 <= len(elem) <= 5
        assert len(set(flatten(sets))) == i
        if i % 5 == 0:
            assert all(len(x) == 5 for x in sets)
        else:
            num_not_five = len([x for x in sets if len(x) != 5])
            if i % 5 == 1 or i % 5 == 2:
                assert num_not_five == 2
            else:
                assert num_not_five == 1


def test_bucket_eliminate_players() -> None:
    bs = SimpleBracketStrategy()
    gr1: TournamentResult = ([], {PlayerID(PlayerID("A")), PlayerID("B")})
    gr2: TournamentResult = ([{PlayerID("C"), PlayerID("D")}, {PlayerID("E")}], set())
    gr3: TournamentResult = (
        [{PlayerID("F")}, set(), {PlayerID("G")}, {PlayerID("H")}],
        {PlayerID("I")},
    )
    r = bs.eliminate_players(
        {
            PlayerID("A"),
            PlayerID("B"),
            PlayerID("C"),
            PlayerID("D"),
            PlayerID("E"),
            PlayerID("F"),
            PlayerID("G"),
            PlayerID("H"),
            PlayerID("I"),
        },
        [gr1, gr2, gr3],
    )
    assert r.is_ok()
    assert r.value() == {PlayerID("A"), PlayerID("B"), PlayerID("H"), PlayerID("I")}

    r = bs.eliminate_players(set(), [gr1])
    assert r.is_error()
    assert (
        r.error()
        == "game results contain a different set of players than the set of live players"
    )

    r = bs.eliminate_players({PlayerID("A"), PlayerID("B"), PlayerID("Z")}, [gr1])
    assert r.is_error()
    assert (
        r.error()
        == "game results contain a different set of players than the set of live players"
    )


def test_flatten_leaderboards() -> None:
    gr1: TournamentResult = ([], {PlayerID("A"), PlayerID("B")})
    gr2: TournamentResult = ([{PlayerID("C"), PlayerID("D")}, {PlayerID("E")}], set())
    gr3: TournamentResult = (
        [{PlayerID("F")}, set(), {PlayerID("G")}, {PlayerID("H")}],
        {PlayerID("I")},
    )
    assert flatten_leaderboards([gr1, gr2, gr3]) == {
        PlayerID("A"),
        PlayerID("B"),
        PlayerID("C"),
        PlayerID("D"),
        PlayerID("E"),
        PlayerID("F"),
        PlayerID("G"),
        PlayerID("H"),
        PlayerID("I"),
    }
