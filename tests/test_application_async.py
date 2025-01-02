import asyncio
from collections.abc import Callable

import pytest

from lato import Application, Command, TransactionContext


@pytest.mark.asyncio
async def test_decorated_async_handler_is_coroutine_function():
    app = Application()

    @app.handler("foo")
    async def foo():
        return 1

    @app.handler("bar")
    def bar():
        return 2

    assert asyncio.iscoroutinefunction(foo) is True
    assert await foo() == 1
    assert asyncio.iscoroutinefunction(bar) is False
    assert bar() == 2


@pytest.mark.asyncio
async def test_call_async_handler():
    app = Application()

    async def async_foo():
        return 1

    result = await app.call_async(async_foo)

    assert result == 1


@pytest.mark.asyncio
async def test_call_async_alias_with_async_context():
    trace = []
    app = Application(trace=trace)

    @app.on_enter_transaction_context
    async def on_enter_transaction_context(ctx: TransactionContext):
        await asyncio.sleep(0.001)
        trace.append("on_enter_transaction_context")

    @app.on_exit_transaction_context
    async def on_exit_transaction_context(ctx, exception):
        await asyncio.sleep(0.001)
        trace.append("on_exit_transaction_context")

    @app.transaction_middleware
    async def async_middleware(ctx: TransactionContext, call_next: Callable):
        await asyncio.sleep(0.001)
        trace.append("before_call_next")
        r = await call_next()
        trace.append("after_call_next")
        return r

    @app.handler("foo")
    async def async_foo():
        await asyncio.sleep(0.001)
        trace.append("async_foo")
        return 1

    result = await app.call_async("foo")

    assert result == 1
    assert trace == [
        "on_enter_transaction_context",
        "before_call_next",
        "async_foo",
        "after_call_next",
        "on_exit_transaction_context",
    ]


@pytest.mark.asyncio
async def test_call_sync_alias_with_async_context():
    trace = []
    app = Application(trace=trace)

    @app.on_enter_transaction_context
    async def on_enter_transaction_context(ctx: TransactionContext):
        await asyncio.sleep(0.001)
        trace.append("on_enter_transaction_context")

    @app.on_exit_transaction_context
    async def on_exit_transaction_context(ctx, exception):
        await asyncio.sleep(0.001)
        trace.append("on_exit_transaction_context")

    @app.handler("foo")
    def async_foo():
        trace.append("sync_foo")

    await app.call_async("foo")

    assert trace == [
        "on_enter_transaction_context",
        "sync_foo",
        "on_exit_transaction_context",
    ]


@pytest.mark.asyncio
async def test_execute_async_command_handler_with_async_context():
    trace = []
    app = Application(trace=trace)

    class FooCommand(Command):
        ...

    @app.on_enter_transaction_context
    async def on_enter_transaction_context(ctx: TransactionContext):
        await asyncio.sleep(0.001)
        trace.append("on_enter_transaction_context")

    @app.on_exit_transaction_context
    async def on_exit_transaction_context(ctx, exception):
        await asyncio.sleep(0.001)
        trace.append("on_exit_transaction_context")

    @app.transaction_middleware
    async def async_middleware(ctx: TransactionContext, call_next: Callable):
        await asyncio.sleep(0.001)
        trace.append("before_call_next")
        r = await call_next()
        trace.append("after_call_next")
        return r

    @app.handler(FooCommand)
    async def async_foo(command: FooCommand):
        await asyncio.sleep(0.001)
        trace.append("async_foo")
        return 1

    result = await app.execute_async(FooCommand())

    assert result == 1
    assert trace == [
        "on_enter_transaction_context",
        "before_call_next",
        "async_foo",
        "after_call_next",
        "on_exit_transaction_context",
    ]


@pytest.mark.asyncio
async def test_call_async_handler_with_sync_context():
    trace = []
    app = Application(trace=trace)

    @app.on_enter_transaction_context
    def on_enter_transaction_context(ctx: TransactionContext):
        trace.append("on_enter_transaction_context")

    @app.on_exit_transaction_context
    def on_exit_transaction_context(ctx, exception):
        trace.append("on_exit_transaction_context")

    async def async_foo():
        await asyncio.sleep(0.001)
        trace.append("async_foo")
        return 1

    result = await app.call_async(async_foo)

    assert result == 1
    assert trace == [
        "on_enter_transaction_context",
        "async_foo",
        "on_exit_transaction_context",
    ]


@pytest.mark.asyncio
async def test_call_async_handler_with_sync_middleware():
    app = Application()

    @app.transaction_middleware
    def sync_middleware(ctx: TransactionContext, call_next: Callable):
        pass

    @app.handler("async_foo")
    async def async_foo():
        await asyncio.sleep(0.001)
        return 1

    with pytest.raises(TypeError):
        # cannot use synchronous middleware with async handler
        await app.call_async("async_foo")
