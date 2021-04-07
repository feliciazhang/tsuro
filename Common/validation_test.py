# pylint: skip-file
import os
from typing import Dict, List

import pytest

from Common.color import ColorString
from Common.player_interface import PlayerInterface
from Common.result import Result, ok
from Common.util import silenced_object
from Common.validation import TYPE_CHECKING_VAR, validate_types
from Player.first_s import FirstS
from Player.player import Player


@validate_types
def f_int(a: int) -> Result[None]:
    print(a)
    return ok(None)


def test_disabled() -> None:
    if TYPE_CHECKING_VAR in os.environ:
        del os.environ[TYPE_CHECKING_VAR]
    assert f_int(2).assert_value() == None
    assert f_int("3").assert_value() == None  # type: ignore


def test_simple_enabled() -> None:
    os.environ[TYPE_CHECKING_VAR] = "True"
    assert f_int(2).assert_value() == None
    r = f_int("3")  # type: ignore
    assert r.is_error()
    assert r.error() == 'type of argument "a" must be int; got str instead'


@validate_types
def f_literal(c: ColorString) -> Result[None]:
    print(c)
    return ok(None)


def test_literal() -> None:
    os.environ[TYPE_CHECKING_VAR] = "True"
    assert f_literal("red").assert_value() == None
    r = f_literal("neon-green")  # type: ignore
    assert r.is_error()
    assert (
        r.error()
        == """the value of argument "c" must be one of ('white', 'black', 'red', 'green', 'blue'); got neon-green instead"""
    )


@validate_types
def f_complex(
    my_list: List[ColorString], my_dict: Dict[str, List[ColorString]]
) -> Result[int]:
    return ok(len(my_list) + sum([len(x) for x in my_dict.values()]))


def test_complex() -> None:
    assert f_complex(["red", "blue"], {}).assert_value() == 2
    r = f_complex(["red", "blue", "notacolor"], {})  # type: ignore
    assert r.is_error()
    assert (
        r.error()
        == "the value of argument \"my_list\"[2] must be one of ('white', 'black', 'red', 'green', 'blue'); got notacolor instead"
    )

    assert f_complex(["white", "blue"], {"foo": ["white", "red"]}).assert_value() == 4
    r = f_complex(
        ["white", "blue"], {"foo": ["white", "turquoise"]}  # type: ignore
    )
    assert r.is_error()
    assert (
        r.error()
        == "the value of argument \"my_dict\"['foo'][1] must be one of ('white', 'black', 'red', 'green', 'blue'); got turquoise instead"
    )


@validate_types
def f_player(player: PlayerInterface) -> Result[None]:
    return ok(None)


def test_silenced_wrapper_class() -> None:
    p = Player(FirstS())
    assert f_player(p).is_ok()
    # Adding the wrapper class doesn't cause type errors
    assert f_player(silenced_object(p)).is_ok()


@validate_types
def f_forwardref(a: "List[str]") -> None:
    return None


def test_resolve_forward_ref() -> None:
    f_forwardref(["a", "b"])
    with pytest.raises(TypeError):
        f_forwardref(["a", "b", 3])  # type: ignore
