"""
A backport of asyncio.run based off of the implementation here:
https://github.com/python/cpython/blob/3.8/Lib/asyncio/runners.py

asyncio.run is only available in python 3.7 but this is a simple backport based off of the 3.7 implementation.
"""
import asyncio
from typing import Coroutine, Optional, Set, Type


def asyncio_run(
    task: Coroutine,  # type: ignore
    debug: bool = False,
    ignored_exceptions: Optional[Set[Type[Exception]]] = None,
) -> None:
    """
    Execute the coroutine and wait for completion.

    This function runs the passed coroutine, taking care of managing the asyncio event loop and finalizing asynchronous
    generators. This function cannot be called when another asyncio event loop is running in the same thread.

    This function always creates a new event loop and closes it at the end. It should be used as a main entry point
    for asyncio programs, and should ideally only be called once.

    Example:

    ```
    async def main():
        await asyncio.sleep(1)
        print('hello')
    asyncio_run(main())
    ```

    :param task:                The coroutine to execute
    :param debug:               If True run the event loop in debug mode
    :param ignored_exceptions:  The set of exceptions classes to silently ignore
    :return:
    """
    if (
        asyncio.events._get_running_loop()  # pylint: disable=protected-access
        is not None
    ):
        raise RuntimeError("asyncio.run() cannot be called from a running event loop")

    if not asyncio.coroutines.iscoroutine(task):
        raise ValueError("a coroutine was expected, got {!r}".format(task))

    loop = asyncio.events.new_event_loop()
    try:
        asyncio.events.set_event_loop(loop)
        loop.set_debug(debug)
        loop.run_until_complete(task)
    finally:
        try:
            _cancel_all_tasks(loop, ignored_exceptions)
            loop.run_until_complete(loop.shutdown_asyncgens())
        finally:
            asyncio.events.set_event_loop(None)
            loop.close()


def _cancel_all_tasks(
    loop: asyncio.AbstractEventLoop,
    ignored_exceptions: Optional[Set[Type[Exception]]] = None,
) -> None:
    """
    Cancel all tasks on the given event loop.

    :param loop:                The loop to cancel all tasks on
    :param ignored_exceptions:  The set of exceptions classes to silently ignore
    :return:                    None
    """
    to_cancel = asyncio.Task.all_tasks(loop)
    if not to_cancel:
        return

    for task in to_cancel:
        task.cancel()

    loop.run_until_complete(
        asyncio.tasks.gather(*to_cancel, loop=loop, return_exceptions=True)
    )

    for task in to_cancel:
        if task.cancelled():
            continue
        if task.exception() is not None:
            exception = task.exception()
            if ignored_exceptions and any(
                isinstance(exception, exception_type)
                for exception_type in ignored_exceptions
            ):
                continue
            loop.call_exception_handler(
                {
                    "message": "unhandled exception during asyncio.run() shutdown",
                    "exception": exception,
                    "task": task,
                }
            )
