from collections.abc import Callable
from functools import reduce
from operator import add, or_
from typing import Any, Optional


def compose(values: tuple[Any, ...], operator: Optional[Callable] = None):
    first = values[0]
    if len(values) == 1:
        return first

    if operator is not None:
        operators = [operator]
    else:
        operators = [or_, add]

    for op in operators:
        try:
            return reduce(op, values)
        except TypeError:
            pass
    raise TypeError("Could not compose, tried", operators)
