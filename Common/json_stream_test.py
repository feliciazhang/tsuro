# pylint: skip-file
from io import StringIO
from typing import Any, Callable
from unittest import mock
from unittest.mock import patch

from Common.json_stream import (
    JSONStream,
    NetworkJSONStream,
    StdinStdoutJSONStream,
    StringJSONStream,
    json_dump,
)
from Common.result import Result
from Common.validation import disable_validation


def test_json_dump() -> None:
    assert json_dump("Ⓐ") == '"\\u24b6"'
    assert json_dump({"a": "b"}) == '{"a": "b"}'
    assert json_dump([1, "a", 3.0]) == '[1, "a", 3.0]'


EXAMPLE_INPUT_STRING = """
{"a": "b"}[1,2]"3"

[4
    , 2]
"""
EXAMPLE_INPUT_DATA = [{"a": "b"}, [1, 2], "3", [4, 2]]


def test_string_json_reader() -> None:
    sjs = StringJSONStream("")
    assert sjs.receive_message().is_error()
    assert list(StringJSONStream("").message_iterator()) == []

    sjs = StringJSONStream('""')
    assert [x.assert_value() for x in sjs.message_iterator()] == [""]

    sjs = StringJSONStream(
        """
    [1,0]
    "a"
    
    {"a": "b"}
    1.0
    """
    )
    assert [x.assert_value() for x in sjs.message_iterator()] == [
        [1, 0],
        "a",
        {"a": "b"},
        1.0,
    ]

    r = sjs.send_message("msg")
    assert r.is_error()
    assert r.error() == "StringJSONStream does not implemented sending of messages"


@patch("sys.stdout", new_callable=StringIO)
@patch("sys.stdin", new_callable=lambda: StringIO(EXAMPLE_INPUT_STRING))
@disable_validation  # typeguard also does weird things with mocking stdin/stdout and it conflicts
def test_stdin_stdout_stream(mock_stdin: Any, mock_stdout: Any) -> None:
    ssjs = StdinStdoutJSONStream()
    assert ssjs.send_message({"a": "b", "c": 1.0}).is_ok()
    assert mock_stdout.getvalue() == '{"a": "b", "c": 1.0}\n'
    assert ssjs.send_message("word").is_ok()
    assert mock_stdout.getvalue() == '{"a": "b", "c": 1.0}\n"word"\n'

    r = ssjs.receive_message()
    assert r.is_ok()
    assert r.value() == EXAMPLE_INPUT_DATA[0]

    r = ssjs.receive_message()
    assert r.is_ok()
    assert r.value() == EXAMPLE_INPUT_DATA[1]

    r = ssjs.receive_message()
    assert r.is_ok()
    assert r.value() == EXAMPLE_INPUT_DATA[2]

    r = ssjs.receive_message()
    assert r.is_ok()
    assert r.value() == EXAMPLE_INPUT_DATA[3]

    r = ssjs.receive_message()
    assert r.is_error()
    assert (
        r.error()
        == "CLOSED_MESSAGE:  cannot read message from stdin because sys.stdin is closed"
    )


@patch("sys.stdout", new_callable=StringIO)
@patch("sys.stdin", new_callable=lambda: StringIO(EXAMPLE_INPUT_STRING))
@disable_validation  # typeguard also does weird things with mocking stdin/stdout and it conflicts
def test_stdin_stdout_stream_iterator(mock_stdin: Any, mock_stdout: Any) -> None:
    ssjs = StdinStdoutJSONStream()
    assert ssjs.send_message({"a": "b", "c": 1.0}).is_ok()
    assert mock_stdout.getvalue() == '{"a": "b", "c": 1.0}\n'
    assert ssjs.send_message("word").is_ok()
    assert mock_stdout.getvalue() == '{"a": "b", "c": 1.0}\n"word"\n'

    assert [x.assert_value() for x in ssjs.message_iterator()] == EXAMPLE_INPUT_DATA


def mocked_recv(data: bytes) -> Callable[[int], bytes]:
    idx = 0

    def recv(num: int) -> bytes:
        nonlocal idx
        ret = data[idx : idx + num]
        idx += num
        return ret

    return recv


@patch("Common.json_stream.socket.socket")
def test_network_stream_client_recv(mock_socket_constructor: Any) -> None:
    mocked_socket = mock_socket_constructor.return_value
    mocked_socket.recv = mocked_recv(EXAMPLE_INPUT_STRING.encode("utf-8"))
    njs = NetworkJSONStream.tcp_client_to("host", 1337)
    r = njs.receive_message()
    assert r.is_ok()
    assert r.value() == EXAMPLE_INPUT_DATA[0]

    r = njs.receive_message()
    assert r.is_ok()
    assert r.value() == EXAMPLE_INPUT_DATA[1]

    r = njs.receive_message()
    assert r.is_ok()
    assert r.value() == EXAMPLE_INPUT_DATA[2]

    r = njs.receive_message()
    assert r.is_ok()
    assert r.value() == EXAMPLE_INPUT_DATA[3]

    r = njs.receive_message()
    assert r.is_error()
    assert (
        r.error()
        == "CLOSED_MESSAGE:  cannot read message from socket because the socket is closed"
    )

    njs.close()
    mocked_socket.close.assert_called_with()


@patch("Common.json_stream.socket.socket")
def test_network_stream_client_recv_iterator(mock_socket_constructor: Any) -> None:
    mocked_socket = mock_socket_constructor.return_value
    mocked_socket.recv = mocked_recv(EXAMPLE_INPUT_STRING.encode("utf-8"))
    njs = NetworkJSONStream.tcp_client_to("host", 1337)

    assert [x.assert_value() for x in njs.message_iterator()] == EXAMPLE_INPUT_DATA

    njs.close()
    mocked_socket.close.assert_called_with()


@patch("Common.json_stream.socket.socket")
def test_network_stream_client_send(mock_socket_constructor: Any) -> None:
    mocked_socket = mock_socket_constructor.return_value
    njs = NetworkJSONStream.tcp_client_to("host", 1337)
    mocked_socket.connect.assert_called_with(("host", 1337))
    assert mocked_socket.sendall.call_args_list == []

    njs.send_message("a")
    njs.send_message({"a": 1, "b": [1, 2, 3]})
    njs.send_message(["Ⓐ"])
    assert mocked_socket.sendall.call_args_list == [
        mock.call(b'"a"'),
        mock.call(b'{"a": 1, "b": [1, 2, 3]}'),
        mock.call(b'["\\u24b6"]'),
    ]


@patch("Common.json_stream.socket.socket")
def test_network_stream_reject_constructor(_: Any) -> None:
    njs = NetworkJSONStream("host", 1337)
    r = njs.send_message("a")
    assert r.is_error()
    assert (
        r.error()
        == "connection is not initialized, cannot send message (ensure that this NetworkJSONStream "
        "was made via one of the factory methods)"
    )
    r = njs.receive_message()
    assert r.is_error()
    assert (
        r.error()
        == "connection is not initialized, cannot receive message (ensure that this "
        "NetworkJSONStream was made via one of the factory methods)"
    )


@patch("Common.json_stream.socket.socket")
def test_network_stream_server(mock_socket_constructor: Any) -> None:
    mocked_socket = mock_socket_constructor.return_value
    mocked_socket.accept.return_value = mocked_socket, "1.2.3.4"
    njs = NetworkJSONStream.tcp_server_on("host", 1337)
    mocked_socket.bind.assert_called_with(("host", 1337))
    mocked_socket.listen.assert_called_with(0)
    mocked_socket.accept.assert_called_with()

    r = njs.send_message("a")
    assert r.is_ok()
    assert mocked_socket.sendall.call_args_list == [mock.call(b'"a"')]

    r = njs.send_message({"a": "Ⓐ", "b": [5, -1, "c"]})
    assert r.is_ok()
    assert mocked_socket.sendall.call_args_list == [
        mock.call(b'"a"'),
        mock.call(b'{"a": "\\u24b6", "b": [5, -1, "c"]}'),
    ]


def test_interface_unimplented() -> None:
    stream = JSONStream()
    r1 = stream.send_message("a")
    assert r1.is_error()
    assert r1.error() == "send_message not implemented in JSONStream interface"

    r2 = stream.receive_message()
    assert r2.is_error()
    assert r2.error() == "receive_message not implemented in JSONStream interface"
