"""
A websocket server that is used to implement automatic refreshing for our GUI. Hosts a websocket
server and distributes messages received in a multiprocessing queue to all connected websocket
clients.

Meant to be interacted with via the `start_websocket_distributor` method.
"""
import asyncio
import logging
import threading
from multiprocessing import Queue
from typing import NoReturn, Set

import websockets

from Common.asyncio_run import asyncio_run
from Common.util import start_auto_terminated_background_process

# A set of connected websocket clients
CONNECTED_LOCK: threading.Lock = threading.Lock()
CONNECTED: Set[websockets.WebSocketClientProtocol] = set()


def message_queue_to_websocket(shared_queue: "Queue[str]") -> NoReturn:
    """
    A function that loops forever and reads strings from the given Queue and distributes them to
    all connected websockets. The set of connected websockets is tracked via the global variable
    CONNECTED. If an exception is raised while sending to a websocket, removes the websocket from
    CONNECTED.

    :param shared_queue:    The shared queue for data that will be read and sent over websockets
    :return:                Never returns (loops infinitely)
    """
    global CONNECTED  # pylint: disable=global-statement
    while True:
        item = shared_queue.get(block=True)
        to_remove = set()
        CONNECTED_LOCK.acquire()
        for socket in CONNECTED:
            try:
                asyncio_run(
                    socket.send(item),
                    ignored_exceptions={websockets.exceptions.ConnectionClosedOK},
                )
            except websockets.exceptions.ConnectionClosedOK:
                logging.info("Failed to send to websocket client due to websocket")
                to_remove.add(socket)
        CONNECTED -= to_remove
        CONNECTED_LOCK.release()


async def track_connected_websockets(
    socket: websockets.WebSocketClientProtocol, _: str
) -> None:
    """
    Adds connected websockets to the global variable CONNECTED and removes them when they disconnect

    :param socket:      The websocket connect
    :param _:           Unused
    :return:            None
    """
    CONNECTED_LOCK.acquire()
    CONNECTED.add(socket)
    CONNECTED_LOCK.release()
    try:
        # Sleep for an arbitrarily long amount of time until they disconnect which will raise an exception
        await asyncio.sleep(10000)
    finally:
        CONNECTED_LOCK.acquire()
        CONNECTED.remove(socket)
        CONNECTED_LOCK.release()


def start_websocket_server() -> NoReturn:
    """
    Start a websocket server that places all connected websockets into the global variable CONNECTED
    :return:    Never returns (loops infinitely)
    """
    start_server = websockets.serve(  # type: ignore
        track_connected_websockets, "localhost", 8765
    )

    asyncio.get_event_loop().run_until_complete(start_server)
    asyncio.get_event_loop().run_forever()
    raise Exception("asyncio event loop completed (this should never happen)!")


def start_websocket_distributor() -> "Queue[str]":
    """
    Start a websocket server in a separate process that passes all strings in a message queue to
    all connected websocket clients. Returns a message queue that is shared between processes.

    :return:                A shared message queue. All strings placed in the message queue will be
                            sent to all connected websocket clients at the time the message is processed.
    """
    shared_queue: "Queue[str]" = Queue()
    start_auto_terminated_background_process(
        target=_start_websocket_distributor, args=(shared_queue,)
    )
    return shared_queue


def _start_websocket_distributor(shared_queue: "Queue[str]") -> NoReturn:
    thread = threading.Thread(target=message_queue_to_websocket, args=(shared_queue,))
    thread.start()
    start_websocket_server()
