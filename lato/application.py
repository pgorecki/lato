from typing import Any, Callable

from lato.application_module import ApplicationModule
from lato.dependency_provider import DependencyProvider
from lato.transaction_context import TransactionContext


class Application(ApplicationModule):
    dependency_provider_class = DependencyProvider

    def __init__(self, name=__name__, dependency_provider=None, **kwargs):
        super().__init__(name)
        self.dependency_provider = (
            dependency_provider or self.dependency_provider_class(**kwargs)
        )
        self._on_enter_transaction_context = lambda ctx: None
        self._on_exit_transaction_context = lambda ctx, exception=None: None
        self._transaction_middlewares = []

    def get_dependency(self, identifier: Any) -> Any:
        """Get a dependency from the dependency provider"""
        return self.dependency_provider.get_dependency(identifier)

    def __getitem__(self, item) -> Any:
        return self.get_dependency(item)

    def call(self, func: Callable | str, *args, **kwargs):
        with self.transaction_context() as ctx:
            result = ctx.call(func, *args, **kwargs)
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

    def transaction_middleware(self, middleware_func):
        """
        Decorator for registering a middleware function to be called when executing a function in a transaction context
        :param middleware_func:
        :return:
        """
        self._transaction_middlewares.insert(0, middleware_func)
        return middleware_func

    def transaction_context(self, **dependencies) -> TransactionContext:
        """
        Creates a transaction context with the application dependencies

        :param dependencies:
        :return:
        """
        dp = self.dependency_provider.copy(**dependencies)
        ctx = TransactionContext(dependency_provider=dp)
        ctx.configure(
            on_enter_transaction_context=self._on_enter_transaction_context,
            on_exit_transaction_context=self._on_exit_transaction_context,
            middlewares=self._transaction_middlewares,
            handlers_iterator=self.iterate_handlers_for,
        )
        return ctx
