from collections.abc import Callable
from functools import partial, reduce
from operator import add, or_
from typing import Any, Optional

from mergedeep import Strategy, merge

additive_merge = partial(merge, strategy=Strategy.TYPESAFE_ADDITIVE)


def compose(compose_operator: Optional[Callable] = None, **kwargs: Any) -> Any:
    values = tuple(value for module_name, value in kwargs.items() if value is not None)

    if len(values) == 0:
        return None

    first = values[0]
    if len(values) == 1:
        return first

    if compose_operator is not None:
        operators = [compose_operator]
    else:
        operators = [additive_merge, or_, add]

    for op in operators:
        try:
            return reduce(op, values)
        except TypeError:
            pass
    raise TypeError("Could not compose", values)
