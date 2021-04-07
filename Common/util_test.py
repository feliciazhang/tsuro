# pylint: skip-file
from typing import Any

import pytest

from Common import util
from Common.result import Result
from Common.util import silenced_object


def test_flatten() -> None:
    assert util.flatten([]) == []
    assert util.flatten([[]]) == []
    assert util.flatten([[1, 2], [3, 4]]) == [1, 2, 3, 4]
    assert util.flatten([(1, 2), (3, 4)]) == [1, 2, 3, 4]


def test_get_tsuro_root_path() -> None:
    assert util.get_tsuro_root_path() != ""
    assert util.get_tsuro_root_path().startswith("/")


def test_random_filename() -> None:
    assert util.random_filename() != util.random_filename()
    assert isinstance(util.random_filename(), str)
    assert util.random_filename().startswith("/tmp/")
    assert util.random_filename().count("/") == 2


class Crasher:
    def method1(self) -> None:
        raise Exception("Exception that is completely dropped")

    def method2(self) -> Result[None]:
        raise Exception("Exception that is passed in a result")

    def method3(self):  # type: ignore
        raise Exception("Exception without a declared return type")

    def method4(self) -> str:
        return "no crash"


def test_silenced_wrapper_class(caplog: Any) -> None:
    crasher = Crasher()
    silenced_crasher = silenced_object(crasher)
    with pytest.raises(Exception):
        crasher.method1()
    with pytest.raises(Exception):
        crasher.method2()
    with pytest.raises(Exception):
        crasher.method3()  # type: ignore
    assert crasher.method4() == "no crash"

    assert crasher == crasher
    assert silenced_crasher == crasher
    assert crasher == silenced_crasher
    assert silenced_crasher == silenced_crasher
    assert hash(crasher) == hash(crasher)
    assert hash(silenced_crasher) == hash(crasher)
    assert hash(crasher) == hash(silenced_crasher)
    assert hash(silenced_crasher) == hash(silenced_crasher)

    assert silenced_crasher.method1() is None  # type: ignore
    r = silenced_crasher.method2()
    assert r.is_error()
    assert r.error() == "Exception that is passed in a result"
    assert silenced_crasher.method3() is None  # type: ignore
    assert "SilencedWrapperClass ignored an exception from" in caplog.text
    assert silenced_crasher.method4() == "no crash"

    with pytest.raises(AttributeError):
        silenced_crasher.doesnt_exist  # type: ignore
