"""
Holds a variety of small general purpose utility functions
"""

import atexit
import logging
import os
import random
import signal
import string
from multiprocessing import Process
from typing import Any, Callable, Iterable, Iterator, List, TypeVar, cast

from Common.result import Result, error

T = TypeVar("T")


def flatten(nested_list: Iterable[Iterable[T]]) -> List[T]:
    """
    Flatten the given nested list
    :param nested_list:     An iterable of iterables
    :return:                A list containing all of the elements in the given iterable of iterables
    """
    return [item for sublist in nested_list for item in sublist]


def chunks(lst: List[T], num: int) -> Iterator[List[T]]:
    """
    Chunk the given list into lists of size num

    :param lst: The list to be chunked
    :param n:   The size of the chunks to generate
    :return:    An iterator of chunks of size N where the final chunk may be of size less than N
    """
    for idx in range(0, len(lst), num):
        yield lst[idx : idx + num]


def get_tsuro_root_path() -> str:
    """
    Get the root path to the top level Tsuro directory

    :return:    The absolute path to the Tsuro directory
    """
    return os.path.dirname(
        os.path.abspath(os.path.join(os.path.realpath(__file__), "../"))
    )


def random_filename() -> str:
    """
    Generate a random filename in /tmp/ for storing files
    :return:    A string containing the filename
    """
    return "/tmp/" + "".join(random.choice(string.ascii_lowercase) for _ in range(10))


def start_auto_terminated_background_process(
    target: Callable[..., Any], args: Any
) -> None:
    """
    Start a process targeting the given function with the given arguments. The process is run in
    the background and is not joined. There is no way to monitor the status of the started
    process or get the return value. Instead, this function provides the guarantee that the
    started process will be terminated prior to the parent function getting terminated.

    :param target:  The function to call
    :param args:    The arguments to pass to the function
    :return:        None
    """
    proc = Process(target=target, args=args)
    proc.start()
    # Use atexit to kill the process when the parent process exits
    atexit.register(proc.terminate)


class timeout:
    # pylint: disable=no-self-use, unused-argument, invalid-name
    """
    A context manager that runs the given code with a timeout. Meant to be used via:

    ```
    with timeout(seconds=1):
        time.sleep(2)
    ```

    Note that this timeout decorator does not handle multiple processes in a safe way and
    if it is being used in a codebase with multiple processes must be used carefully in
    order to ensure all processes are terminated.
    """

    seconds: int

    def __init__(self, seconds: int = 1) -> None:
        self.seconds = seconds

    def _handle_timeout(self, signum: Any, frame: Any) -> None:
        """
        Handle a timeout by raising an exception
        """
        raise TimeoutError("Timeout!")

    def __enter__(self) -> None:
        """
        Enter the context manager and start the timeout period
        """
        signal.signal(signal.SIGALRM, self._handle_timeout)
        signal.alarm(self.seconds)

    def __exit__(self, typ: Any, value: Any, traceback: Any) -> None:
        """
        Exit the context manager and reset the signal
        """
        signal.alarm(0)


def silenced_object(obj: T) -> T:
    """
    Wrap the given object in a wrapper class that will silence all exceptions. As long as no
    methods raise exceptions, the returned object is identical and will compare identically
    (via hash and eq) to the wrapped object.

    :param obj:     The object to wrap
    :return:        The wrapped object
    """
    if isinstance(obj, SilencedWrapperClass):
        return cast(T, obj)
    return cast(T, SilencedWrapperClass(obj))


class SilencedWrapperClass:
    """
    A wrapper class to silence arbitrary wrapped classes. Works via some amount of magic. Meant to
    be interacted with via the `silenced_object` function and not meant to be manually constructed.
    """

    def __init__(self, wrapped: Any) -> None:
        """
        Create a new SilencedWrapperClass that wraps the given object

        :param wrapped:     The object to wrap
        """
        self._wrapped_silenced_object = wrapped

    def __getattr__(self, attr: str) -> Any:
        """
        Get the given attribute on this silenced wrapper class. getattr is called if the attribute is
        not found via normal attribute resolution means. For this class, getattr is called whenever
        someone attempts to access an attribute on the class that this wraps.

        * Raises an AttributeError if the attribute does not exist on the wrapped object
        * Returns the item if the item at the attribute is not a callable
        * Returns a function that wraps the original item if the item at the attribute is a callable.
          The wrapped function silences exceptions. If the original function's signature stated that
          it returned a Result, then any raised exceptions will be passed along as a result. Otherwise,
          exceptions will be logged and ignored.


        :param attr:    The attribute to access
        :return:        The attribute on the wrapped object
        """
        if not hasattr(self._wrapped_silenced_object, attr):
            raise AttributeError(
                f"Failed to access attribute '{attr}' on "
                f"SilencedWrapperClass.wrapped={self._wrapped_silenced_object}"
            )

        item = getattr(self._wrapped_silenced_object, attr)

        if not callable(item):
            return item

        def wrapped(*args: Any, **kwargs: Any) -> Any:
            """
            Wrap item in order to ignore exceptions. Either logs the exception or returns it as a result.
            """
            try:
                return item(*args, **kwargs)
            except Exception as exc:  # pylint: disable=broad-except
                return_type = item.__annotations__.get("return", None)
                if getattr(return_type, "__origin__", None) == Result:
                    return error(str(exc))
                else:
                    logging.warning(
                        f"SilencedWrapperClass ignored an exception from {self._wrapped_silenced_object}. "
                        f"Exception={str(exc)}"
                    )
                    return None

        return wrapped

    def __hash__(self) -> int:
        return hash(self._wrapped_silenced_object)

    def __eq__(self, other: Any) -> bool:
        return cast(bool, self._wrapped_silenced_object == other)
