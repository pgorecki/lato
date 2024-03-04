from collections.abc import Callable
from functools import partial, reduce
from operator import add, or_
from typing import Any, Optional

from mergedeep import Strategy, merge  # type: ignore

additive_merge = partial(merge, strategy=Strategy.TYPESAFE_ADDITIVE)


def compose(values: tuple[Any, ...], operator: Optional[Callable] = None):
    values = tuple(v for v in values if v is not None)

    if len(values) == 0:
        return None

    first = values[0]
    if len(values) == 1:
        return first

    if operator is not None:
        operators = [operator]
    else:
        operators = [additive_merge, or_, add]

    for op in operators:
        try:
            return reduce(op, values)
        except TypeError:
            pass
    raise TypeError("Could not compose", values)
