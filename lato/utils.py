import asyncio
import re
from collections import OrderedDict
from collections.abc import Callable, Iterable
from typing import Any, Optional, TypeVar

T = TypeVar("T")


class OrderedSet(OrderedDict[T, None]):
    def __init__(self, iterable: Optional[Iterable[T]] = None) -> None:
        super().__init__()
        if iterable:
            for item in iterable:
                self.add(item)

    def add(self, item: T) -> None:
        self[item] = None

    def update(self, iterable: Iterable[T]) -> None:  # type: ignore[override]
        for item in iterable:
            self.add(item)


def string_to_kwarg_name(string: str) -> str:
    # Remove invalid characters and replace them with underscores
    valid_string = re.sub(r"[^a-zA-Z0-9_]", "_", string)

    # Ensure the name starts with a letter or underscore
    if not valid_string[0].isalpha() and valid_string[0] != "_":
        valid_string = "_" + valid_string

    return valid_string


async def maybe_await(func: Callable[..., Any], *args: Any, **kwargs: Any) -> Any:
    if asyncio.iscoroutinefunction(func):
        return await func(*args, **kwargs)
    else:
        return func(*args, **kwargs)
