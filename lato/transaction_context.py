from collections import OrderedDict
from collections.abc import Callable, Iterator
from functools import partial
from typing import Any, NewType

from lato.dependency_provider import (
    DependencyProvider,
    SimpleDependencyProvider,
    as_type,
)
from lato.message import Message, Task

Alias = NewType("Alias", Any)


class TransactionContext:
    """A context spanning a single transaction for execution of a function"""

    dependency_provider_factory = SimpleDependencyProvider

    def __init__(
        self, dependency_provider: DependencyProvider | None = None, *args, **kwargs
    ):
        self.dependency_provider = (
            dependency_provider or self.dependency_provider_factory(*args, **kwargs)
        )
        self.resolved_kwargs: dict[str, Any] = {}
        self.current_action: tuple[str | Message, Any] | None = None
        self._on_enter_transaction_context = lambda ctx: None
        self._on_exit_transaction_context = lambda ctx, exception=None: None
        self._middlewares: list[Callable] = []
        self._handlers_iterator: Iterator = lambda alias: iter([])

    def configure(
        self,
        on_enter_transaction_context=None,
        on_exit_transaction_context=None,
        middlewares=None,
        handlers_iterator=None,
    ):
        if on_enter_transaction_context:
            self._on_enter_transaction_context = on_enter_transaction_context
        if on_exit_transaction_context:
            self._on_exit_transaction_context = on_exit_transaction_context
        if middlewares:
            self._middlewares = middlewares
        if handlers_iterator:
            self._handlers_iterator = handlers_iterator

    def begin(self):
        """Should be used to start a transaction"""
        self._on_enter_transaction_context(self)

    def end(self, exception=None):
        """Should be used to commit/end a transaction"""
        self._on_exit_transaction_context(self, exception)

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
        """
        Call a function with the given arguments and keyword arguments.
        Any dependencies will be resolved from the dependency provider.
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

    def execute(self, task: Task) -> tuple[Any, ...]:
        results = self.emit(task)
        values = tuple(results.values())
        if len(values) == 0:
            raise ValueError("No handlers found for task", task)
        return values

    def emit(self, message: str | Message, *args, **kwargs) -> dict[Callable, Any]:
        """Emit a message by calling all handlers for that message"""
        alias = type(message) if isinstance(message, Message) else message

        if isinstance(message, Message):
            args = (message, *args)

        all_results = OrderedDict()
        for handler in self._handlers_iterator(alias):
            # FIXME: push and pop current action instead of setting it
            self.current_action = (message, handler)
            result = self.call(handler, *args, **kwargs)
            all_results[handler] = result
        return all_results

    def get_dependency(self, identifier: Any) -> Any:
        """Get a dependency from the dependency provider"""
        return self.dependency_provider.get_dependency(identifier)

    def set_dependency(self, identifier: Any, dependency: Any) -> None:
        """Set a dependency in the dependency provider"""
        self.dependency_provider.register_dependency(identifier, dependency)

    def __getitem__(self, item) -> Any:
        return self.get_dependency(item)
