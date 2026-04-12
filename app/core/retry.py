import asyncio
from collections.abc import Awaitable, Callable
from typing import TypeVar

T = TypeVar("T")


async def retry_async(
    fn: Callable[[], Awaitable[T]],
    retries: int,
    base_delay: float = 1.0,
    retry_on: tuple[type[Exception], ...] = (Exception,),
) -> T:
    attempt = 0
    while True:
        try:
            return await fn()
        except retry_on:
            if attempt >= retries:
                raise
            await asyncio.sleep(base_delay * (2**attempt))
            attempt += 1
