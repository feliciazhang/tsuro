# pylint: skip-file
import pytest

from Common import result


def test_result() -> None:
    r = result.ok("a")
    assert r.is_ok()
    assert not r.is_error()
    assert r.value() == "a"
    with pytest.raises(result.ResultMisuseException):
        r.error()
    assert str(r) == repr(r) == "Result(val='a')"

    r = result.error("msg")
    assert not r.is_ok()
    assert r.is_error()
    assert r.error() == "msg"
    with pytest.raises(result.ResultMisuseException):
        r.value()
    assert str(r) == repr(r) == "Result(error='msg')"


def test_result_constructor() -> None:
    with pytest.raises(result.ResultMisuseException):
        result.Result()
    with pytest.raises(result.ResultMisuseException):
        result.Result(val="a", error_msg="b")


def test_assert_value() -> None:
    with pytest.raises(AssertionError):
        result.error("error msg").assert_value()


def test_exceptions() -> None:
    with pytest.raises(ValueError):
        result.ok("a") == result.ok("b")
    with pytest.raises(ValueError):
        if result.ok("a"):
            pass
    with pytest.raises(ValueError):
        hash(result.ok("a"))


def test_misuse_result() -> None:
    with pytest.raises(result.ResultMisuseException):
        result.error("crash").error()
    with pytest.raises(result.ResultMisuseException):
        result.ok("yes").value()
