import asyncio
import logging
from collections import OrderedDict
from collections.abc import Awaitable, Callable, Iterator
from dataclasses import dataclass
from functools import partial
from types import TracebackType
from typing import Any, Optional, Union

from lato.compositon import compose
from lato.dependency_provider import (
    BasicDependencyProvider,
    DependencyProvider,
    as_type,
)
from lato.exceptions import HandlerNotFoundError
from lato.message import Message
from lato.types import DependencyIdentifier, HandlerAlias
from lato.utils import maybe_await

log = logging.getLogger(__name__)


@dataclass
class MessageHandler:
    source: str
    message: HandlerAlias
    fn: Callable[..., Any]

    def __hash__(self) -> int:
        return hash((self.source, self.fn))


OnEnterTransactionContextCallback = Callable[..., Any]
OnExitTransactionContextCallback = Callable[..., Any]
MiddlewareFunction = Callable[["TransactionContext", Callable[..., Any]], Any]
ComposerFunction = Callable[..., Any]
HandlersIterator = Callable[[HandlerAlias], Iterator[MessageHandler]]


class TransactionContext:
    """Transaction context is a context manager for handler execution.

    :param dependency_provider_factory: a factory that returns :class:`DependencyProvider` instance,
        defaults to BasicDependencyProvider.

    **Example:**
    >>> from lato import TransactionContext
    >>>
    >>> def my_function(param1, param2):
    ...     print(param1, param2)
    >>>
    >>> with TransactionContext(param1="foo") as ctx:
    ...     ctx.call(my_function, param2="bar")
    foo bar
    """

    dependency_provider_factory = BasicDependencyProvider

    def __init__(
        self,
        dependency_provider: Optional[DependencyProvider] = None,
        *args: Any,
        **kwargs: Any,
    ) -> None:
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
        self.current_handler: Optional[MessageHandler] = None
        self._on_enter_transaction_context: Optional[
            OnEnterTransactionContextCallback
        ] = None
        self._on_exit_transaction_context: Optional[
            OnExitTransactionContextCallback
        ] = None
        self._middlewares: list[MiddlewareFunction] = []
        self._composers: dict[HandlerAlias, ComposerFunction] = {}
        self._handlers_iterator: HandlersIterator = lambda alias: iter([])

    def configure(
        self,
        on_enter_transaction_context: Optional[
            OnEnterTransactionContextCallback
        ] = None,
        on_exit_transaction_context: Optional[OnExitTransactionContextCallback] = None,
        middlewares: Optional[list[MiddlewareFunction]] = None,
        composers: Optional[dict[HandlerAlias, ComposerFunction]] = None,
        handlers_iterator: Optional[HandlersIterator] = None,
    ) -> None:
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

    def begin(self) -> None:
        """Starts a transaction by calling `on_enter_transaction_context` callback.

        The callback could be used to set up the transaction-level dependencies (i.e. current time, transaction id),
        or to start the database transaction.
        """
        log.debug("Transaction started")
        if self._on_enter_transaction_context:
            if asyncio.iscoroutinefunction(self._on_enter_transaction_context):
                raise ValueError(
                    "Using async on_enter_transaction_context callback with synchronous call. Use call_async instead"
                )
            self._on_enter_transaction_context(self)

    async def begin_async(self) -> None:
        """Asynchronously starts a transaction by calling async `on_enter_transaction_context` callback.

        The callback could be used to set up the transaction-level dependencies (i.e. current time, transaction id),
        or to start the database transaction.
        """
        log.debug("Transaction started")
        if self._on_enter_transaction_context:
            result = self._on_enter_transaction_context(self)
            if asyncio.iscoroutine(result):
                await result

    def end(self, exception: Optional[Exception] = None) -> None:
        """Ends the transaction context by calling `on_exit_transaction_context` callback,
        optionally passing an exception.

        The callback could be used to commit/end a database transaction.

        :param exception: Optional; The exception to handle at the end of the transaction, if any.
        """
        if self._on_exit_transaction_context:
            if asyncio.iscoroutinefunction(self._on_exit_transaction_context):
                raise ValueError(
                    "Using async on_exit_transaction_context callback with synchronous call. Use call_async instead"
                )
            self._on_exit_transaction_context(self, exception)

        if exception:
            log.debug("Ended transaction with exception: {}".format(exception))
        else:
            log.debug("Ended transaction")

    async def end_async(self, exception: Optional[Exception] = None) -> None:
        """Ends the transaction context by calling `on_exit_transaction_context` callback,
        optionally passing an exception.

        The callback could be used to commit/end a database transaction.

        :param exception: Optional; The exception to handle at the end of the transaction, if any.
        """
        if self._on_exit_transaction_context:
            result = self._on_exit_transaction_context(self, exception)
            if asyncio.iscoroutine(result):
                await result

        if exception:
            log.debug("Ended transaction with exception: {}".format(exception))
        else:
            log.debug("Ended transaction")

    def is_async_context_manager(self) -> bool:
        """
        Determine if the transaction context requires `async with` context manager.

        This method checks if either the `on_enter` or `on_exit` callbacks
        associated with the transaction context are asynchronous.

        :return: True if `on_enter` or `on_exit` are asynchronous callbacks, False otherwise.
        """
        return any(
            [asyncio.iscoroutinefunction(self._on_enter_transaction_context)]
            + [asyncio.iscoroutinefunction(self._on_exit_transaction_context)]
        )

    def iterate_handlers_for(self, alias: HandlerAlias) -> Iterator[MessageHandler]:
        yield from self._handlers_iterator(alias)

    def __enter__(self) -> "TransactionContext":
        self.begin()
        return self

    def __exit__(
        self,
        exc_type: Optional[type[BaseException]] = None,
        exc_val: Optional[BaseException] = None,
        exc_tb: Optional[TracebackType] = None,
    ) -> None:
        self.end(exc_val)  # type: ignore[arg-type]

    async def __aenter__(self) -> "TransactionContext":
        result = self.begin_async()
        if asyncio.iscoroutine(result):
            await result
        return self

    async def __aexit__(
        self,
        exc_type: Optional[type[BaseException]] = None,
        exc_val: Optional[BaseException] = None,
        exc_tb: Optional[TracebackType] = None,
    ) -> None:
        result = self.end_async(exc_val)  # type: ignore[arg-type]
        if asyncio.iscoroutine(result):
            await result

    def call(
        self, func: Callable[..., Any], *func_args: Any, **func_kwargs: Any
    ) -> Any:
        """Call a function with the arguments and keyword arguments.
        Missing arguments will be resolved with the dependency provider.

        If func is coroutine, or any of the middleware functions is coroutine, TypeError will be raised.

        :param func: The function to call.
        :param func_args: Positional arguments to pass to the function.
        :param func_kwargs: Keyword arguments to pass to the function.
        :return: The result of the function call.
        """
        if asyncio.iscoroutinefunction(func):
            raise TypeError(
                f"Using async function ({func}) with {self.__class__.__name__}.call() is not allowed. Use call_async() instead."
            )

        self.dependency_provider.update(ctx=as_type(self, TransactionContext))

        resolved_kwargs = self.dependency_provider.resolve_func_params(
            func, func_args, func_kwargs
        )
        self.resolved_kwargs.update(resolved_kwargs)

        call_next = partial(func, **resolved_kwargs)

        for m in self._middlewares[::-1]:
            # middleware is async, which is not allowed
            if asyncio.iscoroutinefunction(m):
                raise TypeError(
                    f"Using async middleware ({m}) with {self.__class__.__name__}.call() is not allowed. Use call_async() instead."
                )

            call_next = partial(m, self, call_next)

        return call_next()

    async def call_async(
        self, func: Callable[..., Awaitable[Any]], *func_args: Any, **func_kwargs: Any
    ) -> Any:
        """Call an async function with the arguments and keyword arguments.
        Missing arguments will be resolved with the dependency provider.

        Edge cases:
        - middlewares and func are sync - this will behave like call()
        - middleware is sync, and call_next is async - will raise TypeError, as middleware will not be able to wait for call_next()

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

        call_next = partial(func, **resolved_kwargs)

        for m in self._middlewares[::-1]:
            if asyncio.iscoroutinefunction(m) and not asyncio.iscoroutinefunction(
                call_next
            ):
                # async middleware is expecting an awaitable, so we need convert call_next to async
                call_next = partial(maybe_await, call_next)

            if not asyncio.iscoroutinefunction(m) and asyncio.iscoroutinefunction(
                call_next
            ):
                # middleware is not able to retrieve call_next, as call_next is awaitable
                raise TypeError(
                    f"Using sync middleware ({m}) with async call_next ({call_next}) is not allowed."
                )
            call_next = partial(m, self, call_next)

        if asyncio.iscoroutinefunction(call_next):
            return await call_next()
        else:
            return call_next()

    def execute(self, message: Message) -> Any:
        """Executes all handlers bound to the message. Returns a tuple of handlers' return values.

        :param message: The message to be executed.
        :return: a tuple of return values from executed handlers
        :raises HandlerNotFoundError: If no handlers are found for the message.
        """
        results = self.publish(message)

        if len(results) == 0:
            raise HandlerNotFoundError(f"No handlers found for message: {message}")

        composed_result = self._compose_results(message, results)
        return composed_result

    async def execute_async(self, message: Message) -> Any:
        """Executes all async handlers bound to the message. Returns a tuple of handlers' return values.

        :param message: The message to be executed.
        :return: a tuple of return values from executed handlers
        :raises HandlerNotFoundError: If no handlers are found for the message.
        """
        results = await self.publish_async(message)

        if len(results) == 0:
            raise HandlerNotFoundError(f"No handlers found for message: {message}")

        composed_result = self._compose_results(message, results)
        return composed_result

    def emit(
        self, message: Union[str, Message], *args: Any, **kwargs: Any
    ) -> dict[MessageHandler, Any]:
        # TODO: mark as obsolete
        return self.publish(message, *args, **kwargs)

    def publish(
        self, message: Union[str, Message], *args: Any, **kwargs: Any
    ) -> dict[MessageHandler, Any]:
        """
        Publish a message by calling all handlers for that message.

        :param message: The message object to publish, or an alias of a handler to call.
        :param args: Positional arguments to pass to the handlers.
        :param kwargs: Keyword arguments to pass to the handlers.
        :return: A dictionary mapping handlers to their results.
        """
        message_type = type(message) if isinstance(message, Message) else message

        if isinstance(message, Message):
            args = (message, *args)

        all_results: OrderedDict[MessageHandler, Any] = OrderedDict()
        for handler in self._handlers_iterator(message_type):  # type: ignore[arg-type]
            self.set_dependency("message", message)
            # FIXME: push and pop current action instead of setting it
            self.current_handler = handler
            result = self.call(handler.fn, *args, **kwargs)
            all_results[handler] = result
        return all_results

    async def publish_async(
        self, message: Union[str, Message], *args: Any, **kwargs: Any
    ) -> dict[MessageHandler, Any]:
        """
        Asynchronously publish a message by calling all handlers for that message.

        :param message: The message object to publish, or an alias of a handler to call.
        :param args: Positional arguments to pass to the handlers.
        :param kwargs: Keyword arguments to pass to the handlers.
        :return: A dictionary mapping handlers to their results.
        """
        message_type = type(message) if isinstance(message, Message) else message

        if isinstance(message, Message):
            args = (message, *args)

        all_results: OrderedDict[MessageHandler, Any] = OrderedDict()
        # TODO: use asyncio.gather()
        for handler in self._handlers_iterator(message_type):  # type: ignore[arg-type]
            self.set_dependency("message", message)
            # FIXME: push and pop current action instead of setting it
            self.current_handler = (
                None  # FIXME: multiple handlers can be running asynchronously
            )
            result = await self.call_async(handler.fn, *args, **kwargs)
            all_results[handler] = result
        return all_results

    def get_dependency(self, identifier: DependencyIdentifier) -> Any:
        """Gets a dependency from the dependency provider"""
        return self.dependency_provider.get_dependency(identifier)

    def set_dependency(self, identifier: DependencyIdentifier, dependency: Any) -> None:
        """Sets a dependency in the dependency provider"""
        self.dependency_provider.register_dependency(identifier, dependency)

    def set_dependencies(self, **kwargs: Any) -> None:
        # TODO: add *args
        """Sets multiple dependencies at once"""
        self.dependency_provider.update(**kwargs)

    def __getitem__(self, item: DependencyIdentifier) -> Any:
        return self.get_dependency(item)

    def _compose_results(
        self, message: Message, results: dict[MessageHandler, Any]
    ) -> Any:
        alias = message.__class__  # TODO: expose alias as static field in Message class
        composer = self._composers.get(alias, compose)
        # TODO: there may be multiple values for one source, it this case we should raise an exception and
        # instruct developer to implement a composer on a source level
        kwargs = {k.source: v for k, v in results.items()}
        return composer(**kwargs)

    @property
    def current_action(self) -> tuple[Message, Callable[..., Any]]:
        """Returns current message and handler being executed"""
        return self.get_dependency("message"), self.current_handler  # type: ignore[return-value]
