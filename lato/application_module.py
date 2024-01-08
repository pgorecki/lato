from collections import defaultdict
from collections.abc import Callable

from lato.message import Event, Task
from lato.utils import OrderedSet

import logging
log = logging.getLogger(__name__)


class ApplicationModule:
    def __init__(self, name: str):
        self.name: str = name
        self._handlers: defaultdict[str, OrderedSet[Callable]] = defaultdict(OrderedSet)
        self._submodules: OrderedSet[ApplicationModule] = OrderedSet()

    def include_submodule(self, a_module: "ApplicationModule"):
        assert isinstance(
            a_module, ApplicationModule
        ), f"Can only include {ApplicationModule} instances, got {a_module}"
        self._submodules.add(a_module)

    def handler(self, alias):
        """
        Decorator for registering tasks
        """
        try:
            is_task_or_event = issubclass(alias, (Task, Event))
        except TypeError:
            is_task_or_event = False

        if callable(alias) and not is_task_or_event:
            # @app.handle(my_function)
            func = alias
            alias = func.__name__
            assert len(self._handlers[alias]) == 0
            self._handlers[alias].add(func)
            return func

        # @app.handle("my_function")
        # @app.handle(MyTask)
        def decorator(func):
            """
            Decorator for registering tasks by name
            """
            assert len(self._handlers[alias]) == 0
            self._handlers[alias].add(func)
            return func

        return decorator

    def iterate_handlers_for(self, alias: str):
        if alias in self._handlers:
            for handler in self._handlers[alias]:
                yield handler
        for submodule in self._submodules:
            try:
                yield from submodule.iterate_handlers_for(alias)
            except KeyError:
                pass

    def get_handlers_for(self, alias: str):
        return list(self.iterate_handlers_for(alias))

    def on(self, event_name):
        # TODO: add matcher parameter
        def decorator(func):
            self._handlers[event_name].add(func)
            return func

        return decorator

    def __repr__(self):
        return f"<{self.name} {object.__repr__(self)}>"
