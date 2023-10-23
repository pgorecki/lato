from collections import defaultdict

from utils import OrderedSet


class ApplicationModule:
    def __init__(self, name: str):
        self.name: str = name
        self._handlers: dict[str, set[callable]] = defaultdict(OrderedSet)
        self._submodules: OrderedSet[ApplicationModule] = OrderedSet()

    def include_submodule(self, a_module):
        assert isinstance(
            a_module, ApplicationModule
        ), f"Can only include {ApplicationModule} instances, got {a_module}"
        self._submodules.add(a_module)

    def handler(self, alias):
        """
        Decorator for registering use cases by name
        """
        if callable(alias):
            func = alias
            alias = func.__name__
            assert len(self._handlers[alias]) == 0
            self._handlers[alias].add(func)
            return func

        def decorator(func):
            """
            Decorator for registering use cases by name
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

    def on(self, event_name):
        # TODO: add matcher parameter
        def decorator(func):
            """
            Decorator for registering an event handler

            :param event_handler:
            :return:
            """
            self._handlers[event_name].add(func)
            return func

        return decorator

    def __repr__(self):
        return f"<{self.name} {object.__repr__(self)}>"
