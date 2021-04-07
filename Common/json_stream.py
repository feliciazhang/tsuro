"""
A module containing a series of utility functions and classes responsible for handling reading and
writing JSON values to a variety of input and outputs sources and sinks.
"""
import json
import socket
import sys
from io import StringIO
from typing import Iterator, List, Optional

from Common.result import Result, error, ok
from Common.tsuro_types import JSON
from Common.validation import validate_types

CLOSED_INPUT_PREFIX = "CLOSED_MESSAGE: "


def json_dump(msg: JSON) -> str:
    """
    Dump the given JSON value to a string in a manner that preserves unicode
    :param msg:     The JSON message to dump
    :return:        The string encoding of the given JSON value
    """
    return json.dumps(msg, ensure_ascii=True)


class JSONStream:
    # pylint: disable=no-self-use, unused-argument
    """
    Represents an abstract class for JSON streams that read and write JSON values
    """

    def send_message(self, msg: JSON) -> Result[None]:
        """
        Send the given JSON value over this JSON stream
        :param msg:     The JSON value to send
        :return:        A result indicating whether or not it was sent successfully
        """
        return error("send_message not implemented in JSONStream interface")

    def receive_message(self) -> Result[JSON]:
        """
        Receive a JSON message from this JSON stream
        :return:    A Result containing the received JSON message or an error. The error contains the string
                    `CLOSED_INPUT_PREFIX` if the error is due to a closed input
        """
        return error("receive_message not implemented in JSONStream interface")

    @validate_types
    def message_iterator(self) -> Iterator[Result[JSON]]:
        """
        Returns an iterator that reads JSON messages from this JSON stream
        :return:    An iterator of results of JSON messages. Raises a stop iteration exception if there
                    are no more messages to be read from this JSON stream
        """
        while True:
            msg_r = self.receive_message()
            if (
                msg_r.is_error()
                and CLOSED_INPUT_PREFIX
                in msg_r.error()  # pylint: disable=unsupported-membership-test
            ):
                # The input stream was closed so stop iteration
                return
            yield msg_r


class StdinStdoutJSONStream(JSONStream):
    """
    A JSONStream implementation that reads from stdin and writes to stdout
    """

    @validate_types
    def send_message(self, msg: JSON) -> Result[None]:
        """
        Send the given JSON value to stdout via this JSON stream
        :param msg:     The JSON value to send
        :return:        A result indicating whether or not it was sent successfully
        """
        print(json_dump(msg))
        return ok(None)

    @validate_types
    def receive_message(self) -> Result[JSON]:
        """
        Receive a JSON message from stdin via this JSON stream
        :return:    A Result containing the received JSON message or an error. The error contains the string
                    `CLOSED_INPUT_PREFIX` if the error is due to a closed input
        """
        data = ""
        while True:
            new_char = sys.stdin.read(1)
            if new_char == "":
                return error(
                    f"{CLOSED_INPUT_PREFIX} cannot read message from stdin because sys.stdin is closed"
                )
            data += new_char
            try:
                return ok(json.loads(data))
            except json.JSONDecodeError:
                pass


class NetworkJSONStream(JSONStream):
    """
    A JSONStream implementation that reads and writes to a TCP network socket
    """

    def __init__(self, host: str, port: int) -> None:
        """
        Create a new NetworkJSONStream that is connected to a server via a TCP connection at
        the specified host and port.

        Meant to be a private constructor. Use the static factory methods to make a NetworkJSONStream
        that acts as either a client or as a server.

        :param host:    The host (eg an IP address or a domain name) for the TCP socket
        :param port:    The port for the TCP socket
        """
        self.host = host
        self.port = port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.conn: Optional[socket.socket] = None

    @staticmethod
    def tcp_client_to(host: str, port: int) -> "NetworkJSONStream":
        """
        Start a NetworkJSONStream that is a connection to a remote server.

        :param host:    The host (eg an IP address or a domain name) of the server to connect to
        :param port:    The port to start the TCP connection over
        :return:        A NetworkJSONStream that is connected to a remote server
        """
        njs = NetworkJSONStream(host, port)
        njs.sock.connect((host, port))
        njs.conn = njs.sock
        return njs

    @staticmethod
    def tcp_server_on(host: str, port: int) -> "NetworkJSONStream":
        """
        Start a NetworkJSONStream that is a TCP server waiting for a single connection. Note that
        this method hands until a client connects.

        :param host:    The host for the TCP server
        :param port:    The port for the TCP server
        :return:        A NetworkJSONStream that listens for a single connection
        """
        njs = NetworkJSONStream(host, port)
        njs.sock.bind((host, port))
        njs.sock.listen(0)
        conn, _ = njs.sock.accept()
        njs.conn = conn
        return njs

    @validate_types
    def send_message(self, msg: JSON) -> Result[None]:
        """
        Send the given JSON value to a remote server via this JSON stream
        :param msg:     The JSON value to send
        :return:        A result indicating whether or not it was sent successfully
        """
        if self.conn is None:
            return error(
                "connection is not initialized, cannot send message (ensure that this NetworkJSONStream was "
                "made via one of the factory methods)"
            )
        send_from_conn(self.conn, msg)
        return ok(None)

    @validate_types
    def receive_message(self) -> Result[JSON]:
        """
        Receive a JSON message from a remote server via this JSON stream
        :return:    A Result containing the received JSON message or an error. The error contains the string
                    `CLOSED_INPUT_PREFIX` if the error is due to a closed input
        """
        if self.conn is None:
            return error(
                "connection is not initialized, cannot receive message (ensure that this NetworkJSONStream "
                "was made via one of the factory methods)"
            )
        return rcv_from_conn(self.conn)

    def close(self) -> None:
        """
        Close this NetworkJSONStream in both directions
        :return:    None
        """
        if self.conn:
            close_conn(self.conn)


class StringJSONStream(JSONStream):
    """
    A JSON stream that allows one to read from a string. Note that this JSON stream does not
    support sending messages (for obvious reasons).
    """

    def __init__(self, string: str) -> None:
        """
        Make a JSON stream that wraps around the given string

        :param string:  The string to wrap
        """
        self.string_io = StringIO(string)

    @validate_types
    def receive_message(self) -> Result[JSON]:
        """
        Receive a JSON message from the string inside this JSON stream
        :return:    A Result containing the received JSON message or an error. The error contains the string
                    `CLOSED_INPUT_PREFIX` if the error is due to a closed input
        """
        data = ""
        while True:
            new_char = self.string_io.read(1)
            if new_char == "":
                return error(
                    f"{CLOSED_INPUT_PREFIX} cannot read message from stdin because sys.stdin is closed"
                )
            data += new_char
            try:
                return ok(json.loads(data))
            except json.JSONDecodeError:
                pass

    @validate_types
    def send_message(self, msg: JSON) -> Result[None]:
        """
        Return an error since StringJSONStream does not support sending a message
        :param _:   A message that is not sent
        :return:    A result containing an error
        """
        return error("StringJSONStream does not implemented sending of messages")

####### Socket connection utilities to send/receive/close connections
@validate_types
def send_from_conn(conn, msg:JSON) -> Result[None]:
    """
    Sends the given JSON message using the given connectioin
    """
    conn.sendall(json_dump(msg).encode("utf-8"))

@validate_types
def rcv_from_conn(conn) -> Result[JSON]:
    """
    Receives a message using the given connection
    """
    all_data: List[bytes] = []
    while True:
        data = conn.recv(1)
        if not data:
            return error(
                f"{CLOSED_INPUT_PREFIX} cannot read message from socket because "
                f"the socket is closed"
            )
        all_data.append(data)
        try:
            return ok(json.loads(b"".join(all_data).decode("utf-8")))
        except json.JSONDecodeError:
            pass

@validate_types
def close_conn(conn) -> None:
    """
    Closes the given connection
    """
    conn.shutdown(socket.SHUT_RDWR)
    conn.close()
