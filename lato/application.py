import logging
from collections.abc import Callable
from typing import Any

from lato.application_module import ApplicationModule
from lato.dependency_provider import BasicDependencyProvider, DependencyProvider
from lato.message import Event, Command, Message
from lato.transaction_context import TransactionContext

log = logging.getLogger(__name__)


class Application(ApplicationModule):
    """Core Application class.

    This class represents the core functionality of an application and extends :class:`ApplicationModule`.
    
    :param dependency_provider_factory: a factory that returns :class:`DependencyProvider` instance, 
        defaults to BasicDependencyProvider.
    """
    dependency_provider_factory: type[DependencyProvider] = BasicDependencyProvider

    def __init__(self, name=__name__, dependency_provider: DependencyProvider | None = None, **kwargs):
        """Initialize the application instance.
        
        :param name: Name of the application
        :param dependency_provider: dependency provider :class:`DependencyProvider` instance.
                                    Defaults to :class:`BasicDependencyProvider` instance populated with kwargs.
        :param kwargs: Additional keyword arguments to be passed to the dependency provider.
          
        """
        super().__init__(name)
        self.dependency_provider = (
            dependency_provider or self.dependency_provider_factory(**kwargs)
        )
        self._transaction_context_factory = None
        self._on_enter_transaction_context = lambda ctx: None
        self._on_exit_transaction_context = lambda ctx, exception=None: None
        self._transaction_middlewares = []
        self._composers: dict[str | Command, Callable] = {}

    def get_dependency(self, identifier: str | type) -> Any:
        """Gets a dependency from the dependency provider. Dependencies can be resolved either by name or by type.
        
        :param identifier: A string or a type representing the dependency.
        
        :return: The resolved dependency.
        """
        return self.dependency_provider.get_dependency(identifier)

    def __getitem__(self, identifier: str | type) -> Any:
        return self.get_dependency(identifier)

    def call(self, func: Callable | str, *args, **kwargs):
        """Invokes a function with `args` and `kwargs` within the :class:`TransactionContext`.
        If `func` is a string, then it is an alias, and the corresponding handler for the alias is retrieved.
        Any missing arguments are provided by the dependency provider of a transaction context, 
        and args and kwargs parameters.
        
        :param func: The function to invoke, or an alias.
        :param args: Arguments to pass to the function.
        :param kwargs: Keyword arguments to pass to the function.
        
        :return: The result of the invoked function.
        
        :raises ValueError: If an alias is provided, but no corresponding handler is found.
        """
        if isinstance(func, str):
            try:
                func = next(self.iterate_handlers_for(alias=func))
            except StopIteration:
                raise ValueError(f"Handler not found", func)

        with self.transaction_context() as ctx:
            result = ctx.call(func, *args, **kwargs)
        return result

    def execute(self, message: Message) -> Any:
        """Executes a command within the :class:`TransactionContext`. 
        Use :func:`handler` decorator to register a handler for the command.
        If a command is handled by multiple handlers, then the final result is 
        composed to a single return value using :func:`compose` decorator.
        
        :param message: The message to be executed (usually, a :class:`Command` or :class:`Query` subclass).
        :return: The result of the invoked message handler.
        
        :raises: ValueError: If no handlers are found for the message.
        """
        with self.transaction_context() as ctx:
            result = ctx.execute(message)
            return result

    def emit(self, event: Event) -> dict[Callable, Any]:
        """Deprecated. Use `publish()` instead."""
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
        Decorator for composing results of handlers identified by an alias
        """

        def decorator(func):
            self._composers[alias] = func
            return func

        return decorator

    def transaction_context(self, **dependencies) -> TransactionContext:
        """Creates a transaction context for the app.
        
        The lifecycle of a transaction context is controlled by :func:`transaction_middleware`, 
        :func:`on_enter_transaction_context`, :func:`on_exit_transaction_context` decorators.

        :param dependencies: Keyword arguments to be passed as dependencies to the dependency provider of a transaction
            context, will override dependencies provided by the application.
        :return: transaction context
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
            composers=self._composers,
            handlers_iterator=self.iterate_handlers_for,
        )
        return ctx
