import logging
from collections import defaultdict
from collections.abc import Callable

from lato.message import Message
from lato.types import HandlerAlias
from lato.utils import OrderedSet

log = logging.getLogger(__name__)


class ApplicationModule:
    def __init__(self, name: str):
        """Initialize the application module instance.

        :param name: Name of the module
        """
        self.name: str = name
        self._handlers: defaultdict[str, OrderedSet[Callable]] = defaultdict(OrderedSet)
        self._submodules: OrderedSet[ApplicationModule] = OrderedSet()

    def include_submodule(self, a_module: "ApplicationModule"):
        """Adds a child submodule to this module.

        :param a_module: child module to add
        """
        assert isinstance(
            a_module, ApplicationModule
        ), f"Can only include {ApplicationModule} instances, got {a_module}"
        self._submodules.add(a_module)

    def handler(self, alias: HandlerAlias):
        """
        Decorator for registering a handler. Handler can be aliased by a name or by a message type.

        :param alias: :class:`lato.Message` or a string.

        Example #1:
        -----------
        >>> from lato import Application, ApplicationModule
        >>> my_module = ApplicationModule("my_module")
        >>>
        >>> @my_module.handler("my_handler")
        ... def my_handler():
        ...     print("handler called")
        >>>
        >>> app = Application("example")
        >>> app.include_submodule(my_module)
        >>> app.call("my_handler")
        handler called

        Example #2:
        -----------
        >>> from lato import ApplicationModule, Command
        >>> class MyCommand(Command):
        ...     pass
        >>>
        >>> my_module = ApplicationModule("my_module")
        >>> @my_module.handler(MyCommand)
        ... def my_handler(command: MyCommand):
        ...     print("command handler called")
        >>>
        >>> app = Application("example")
        >>> app.include_submodule(my_module)
        >>> app.execute(MyCommand())
        command handler called
        """
        if isinstance(alias, type):
            is_message_type = issubclass(alias, Message)
        else:
            is_message_type = False

        if callable(alias) and not is_message_type:
            # decorator was called without any argument
            func = alias
            alias = func.__name__
            assert len(self._handlers[alias]) == 0
            self._handlers[alias].add(func)
            return func

        # decorator was called with argument
        # @my_module.handle("my_function")
        # @my_module.handle(MyCommand)
        def decorator(func):
            """
            Decorator for registering tasks by name
            """
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

    def __repr__(self):
        return f"<{self.name} {object.__repr__(self)}>"
