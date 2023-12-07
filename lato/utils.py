from collections import OrderedDict
from typing import TypeVar

T = TypeVar("T")


class OrderedSet(OrderedDict[T, None]):
    def __init__(self, iterable=None):
        super().__init__()
        if iterable:
            for item in iterable:
                self.add(item)

    def add(self, item: T):
        self[item] = None

    def update(self, iterable):
        for item in iterable:
            self.add(item)
