import logging
from collections import OrderedDict
from collections.abc import Callable, Iterator
from functools import partial
from typing import Any, NewType, Optional

from lato.compositon import compose
from lato.dependency_provider import (
    BasicDependencyProvider,
    DependencyProvider,
    as_type,
)
from lato.message import Message

Alias = NewType("Alias", Any)

log = logging.getLogger(__name__)


class TransactionContext:
    """Transaction context is a context manager for handler execution.

    :param dependency_provider_factory: a factory that returns :class:`DependencyProvider` instance,
        defaults to BasicDependencyProvider.

    **Example:**

    >>> from lato import TransactionContext
    >>>
    >>> def my_function(param1, param2):
    >>>     print(param1, param2)
    >>>
    >>> with TransactionContext(param1="foo") as ctx:
    >>>     ctx.call(my_function, param2="bar")
    foo, bar
    """

    dependency_provider_factory = BasicDependencyProvider

    def __init__(
        self, dependency_provider: DependencyProvider | None = None, *args, **kwargs
    ):
        """Initialize the transaction context instance.

        :param dependency_provider: dependency provider :class:`DependencyProvider` instance.
            Defaults to :class:`BasicDependencyProvider` instance populated with args and kwargs.
        :param args: Additional positional arguments to be passed to the dependency provider.
        :param kwargs: Additional keyword arguments to be passed to the dependency provider.
        """

        self.dependency_provider = (
            dependency_provider or self.dependency_provider_factory(*args, **kwargs)
        )
        self.resolved_kwargs: dict[str, Any] = {}
        self.current_handler: Optional[Callable] = None
        self._on_enter_transaction_context = lambda ctx: None
        self._on_exit_transaction_context = lambda ctx, exception=None: None
        self._middlewares: list[Callable] = []
        self._composers: dict[str | Message, Callable] = {}
        self._handlers_iterator: Iterator = lambda alias: iter([])

    def configure(
        self,
        on_enter_transaction_context=None,
        on_exit_transaction_context=None,
        middlewares=None,
        composers=None,
        handlers_iterator=None,
    ):
        """Customize the behavior of the transaction context with callbacks, middlewares, and composers.

        :param on_enter_transaction_context: Optional; Function to be called when entering a transaction context.
        :param on_exit_transaction_context: Optional; Function to be called when exiting a transaction context.
        :param middlewares: Optional; List of middleware functions to be applied.
        :param composers: Optional; List of composers functions to be applied.
        :param handlers_iterator: Optional; Function to iterate over handlers.
        """
        if on_enter_transaction_context:
            self._on_enter_transaction_context = on_enter_transaction_context
        if on_exit_transaction_context:
            self._on_exit_transaction_context = on_exit_transaction_context
        if middlewares:
            self._middlewares = middlewares
        if composers:
            self._composers = composers
        if handlers_iterator:
            self._handlers_iterator = handlers_iterator

    def begin(self):
        """Starts a transaction by calling `on_enter_transaction_context` callback.

        The callback could be used to set up the transaction-level dependencies (i.e. current time, transaction id),
        or to start the database transaction.
        """
        log.debug("Beginning transaction")
        """Should be used to start a transaction"""
        self._on_enter_transaction_context(self)

    def end(self, exception: Exception = None):
        """Ends the transaction context by calling `on_exit_transaction_context` callback,
        optionally passing an exception.

        The callback could be used to commit/end a database transaction.

        :param exception: Optional; The exception to handle at the end of the transaction, if any.
        """
        self._on_exit_transaction_context(self, exception)

        if exception:
            log.debug("Ended transaction with exception: {}".format(exception))
        else:
            log.debug("Ended transaction")

    def iterate_handlers_for(self, alias: str):
        yield from self._handlers_iterator(alias)

    def __enter__(self):
        self.begin()
        return self

    def __exit__(self, exc_type=None, exc_val=None, exc_tb=None):
        self.end(exc_val)

    def _wrap_with_middlewares(self, handler_func):
        p = handler_func
        for middleware in self._middlewares:
            p = partial(middleware, self, p)
        return p

    def call(self, func: Callable, *func_args: Any, **func_kwargs: Any) -> Any:
        """Call a function with the arguments and keyword arguments.
        Missing arguments will be resolved with the dependency provider.

        :param func: The function to call.
        :param func_args: Positional arguments to pass to the function.
        :param func_kwargs: Keyword arguments to pass to the function.
        :return: The result of the function call.
        """
        self.dependency_provider.update(ctx=as_type(self, TransactionContext))

        resolved_kwargs = self.dependency_provider.resolve_func_params(
            func, func_args, func_kwargs
        )
        self.resolved_kwargs.update(resolved_kwargs)
        p = partial(func, **resolved_kwargs)
        wrapped_handler = self._wrap_with_middlewares(p)
        result = wrapped_handler()
        return result

    def execute(self, message: Message) -> tuple[Any, ...]:
        """Executes all handlers bound to the message. Returns a tuple of handlers' return values.

        :param message: The message to be executed.
        :return: a tuple of return values from executed handlers
        :raises: ValueError: If no handlers are found for the message.
        """
        results = self.publish(message)
        values = tuple(results.values())

        if len(values) == 0:
            raise ValueError("No handlers found for message", values)

        composed_result = self._compose_results(message, values)
        return composed_result

    def emit(self, message: str | Message, *args, **kwargs) -> dict[Callable, Any]:
        # TODO: mark as obsolete
        return self.publish(message, *args, **kwargs)

    def publish(self, message: str | Message, *args, **kwargs) -> dict[Callable, Any]:
        """
        Publish a message by calling all handlers for that message.

        :param message: The message object to publish, or a string.
        :param args: Positional arguments to pass to the handlers.
        :param kwargs: Keyword arguments to pass to the handlers.
        :return: A dictionary mapping handlers to their results.
        """
        alias = type(message) if isinstance(message, Message) else message

        if isinstance(message, Message):
            args = (message, *args)

        all_results = OrderedDict()
        for handler in self._handlers_iterator(alias):
            self.set_dependency("message", message)
            # FIXME: push and pop current action instead of setting it
            self.current_handler = handler
            result = self.call(handler, *args, **kwargs)
            all_results[handler] = result
        return all_results

    def get_dependency(self, identifier: Any) -> Any:
        """Gets a dependency from the dependency provider"""
        return self.dependency_provider.get_dependency(identifier)

    def set_dependency(self, identifier: Any, dependency: Any) -> None:
        """Sets a dependency in the dependency provider"""
        self.dependency_provider.register_dependency(identifier, dependency)

    def set_dependencies(self, **kwargs):
        # TODO: add *args
        """Sets multiple dependencies at once"""
        self.dependency_provider.update(**kwargs)

    def __getitem__(self, item) -> Any:
        return self.get_dependency(item)

    def _compose_results(self, message: Message, results: tuple[Any, ...]) -> Any:
        alias = message.__class__  # TODO: expose alias as static field in Message class
        composer = self._composers.get(alias, compose)
        return composer(results)

    @property
    def current_action(self) -> tuple[Message, Callable]:
        """Returns current message and handler being executed"""
        return self.get_dependency("message"), self.current_handler
