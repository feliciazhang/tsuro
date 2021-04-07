# pylint: skip-file
from Common.asyncio_run import asyncio_run


def test_asyncio_run() -> None:
    # A simple sanity test for the happy case
    TASK_HAS_BEEN_RUN = False

    async def example_task() -> None:
        nonlocal TASK_HAS_BEEN_RUN
        TASK_HAS_BEEN_RUN = True

    asyncio_run(example_task())
    assert TASK_HAS_BEEN_RUN == True
