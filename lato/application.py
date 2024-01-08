from collections.abc import Callable
from typing import Any

from lato.application_module import ApplicationModule
from lato.compositon import compose
from lato.dependency_provider import SimpleDependencyProvider
from lato.message import Event, Task
from lato.transaction_context import TransactionContext

import logging
log = logging.getLogger(__name__)


class Application(ApplicationModule):
    dependency_provider_class = SimpleDependencyProvider

    def __init__(self, name=__name__, dependency_provider=None, **kwargs):
        super().__init__(name)
        self.dependency_provider = (
            dependency_provider or self.dependency_provider_class(**kwargs)
        )
        self._transaction_context_factory = None
        self._on_enter_transaction_context = lambda ctx: None
        self._on_exit_transaction_context = lambda ctx, exception=None: None
        self._transaction_middlewares = []
        self._composers: dict[str | Task, Callable] = {}

    def get_dependency(self, identifier: Any) -> Any:
        """Get a dependency from the dependency provider"""
        return self.dependency_provider.get_dependency(identifier)

    def __getitem__(self, item) -> Any:
        return self.get_dependency(item)

    def call(self, func: Callable | str, *args, **kwargs):
        if isinstance(func, str):
            try:
                func = next(self.iterate_handlers_for(alias=func))
            except StopIteration:
                raise ValueError(f"Handler not found", func)

        with self.transaction_context() as ctx:
            result = ctx.call(func, *args, **kwargs)
        return result

    def execute(self, task: Task) -> tuple[Any, ...]:
        with self.transaction_context() as ctx:
            results = ctx.execute(task)
            return results

    def query(self, task: Task) -> Any:
        results = self.execute(task)
        alias = task.__class__
        composer = self._composers.get(alias, compose)
        return composer(results)

    def emit(self, event: Event) -> dict[Callable, Any]:
        with self.transaction_context() as ctx:
            result = ctx.emit(event)
        return result

    def on_enter_transaction_context(self, func):
        """
        Decorator for registering a function to be called when entering a transaction context

        :param func:
        :return:
        """
        self._on_enter_transaction_context = func
        return func

    def on_exit_transaction_context(self, func):
        """
        Decorator for registering a function to be called when exiting a transaction context

        :param func:
        :return:
        """
        self._on_exit_transaction_context = func
        return func

    def on_create_transaction_context(self, func):
        """
        Decorator for overriding default transaction context creation

        :param func:
        :return:
        """
        self._transaction_context_factory = func
        return func

    def transaction_middleware(self, middleware_func):
        """
        Decorator for registering a middleware function to be called when executing a function in a transaction context
        :param middleware_func:
        :return:
        """
        self._transaction_middlewares.insert(0, middleware_func)
        return middleware_func

    def compose(self, alias):
        """
        Decorator for composing results of tasks
        """

        def decorator(func):
            self._composers[alias] = func
            return func

        return decorator

    def transaction_context(self, **dependencies) -> TransactionContext:
        """
        Creates a transaction context with the application dependencies

        :param dependencies:
        :return:
        """
        if self._transaction_context_factory:
            ctx = self._transaction_context_factory(**dependencies)
        else:
            dp = self.dependency_provider.copy(**dependencies)
            ctx = TransactionContext(dependency_provider=dp)

        ctx.configure(
            on_enter_transaction_context=self._on_enter_transaction_context,
            on_exit_transaction_context=self._on_exit_transaction_context,
            middlewares=self._transaction_middlewares,
            handlers_iterator=self.iterate_handlers_for,
        )
        return ctx
