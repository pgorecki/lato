from lato import TransactionContext
import pytest
import itertools
import asyncio


def enter_hook_fn(ctx):
    ctx['call_log'].append("sync_enter")


async def async_enter_hook_fn(ctx):
    await asyncio.sleep(0.02)
    ctx['call_log'].append("async_enter")
    
    
def exit_hook_fn(ctx, exc=None):
    ctx['call_log'].append("sync_exit")


async def async_exit_hook_fn(ctx, exc=None):
    await asyncio.sleep(0.01)
    ctx['call_log'].append("async_exit")


def middleware1_fn(ctx, call_next):
    ctx['call_log'].append("sync_middleware1_enter")
    result = call_next()
    ctx['call_log'].append(f"sync_middleware1_exit with {type(result).__name__}")
    return f"1:{result}:1"
    
    
async def async_middleware1_fn(ctx, call_next):
    await asyncio.sleep(0.01)
    ctx['call_log'].append("async_middleware1_enter")
    await asyncio.sleep(0.01)
    result = await call_next()
    await asyncio.sleep(0.01)
    ctx['call_log'].append(f"async_middleware1_exit with {type(result).__name__}")
    await asyncio.sleep(0.01)
    return f"1:{result}:1"


def middleware2_fn(ctx, call_next):
    ctx['call_log'].append("sync_middleware2_enter")
    result = call_next()
    ctx['call_log'].append(f"sync_middleware2_exit with {type(result).__name__}")
    return f"2:{result}:2"


async def async_middleware2_fn(ctx, call_next):
    await asyncio.sleep(0.01)
    ctx['call_log'].append("async_middleware2_enter")
    await asyncio.sleep(0.01)
    result = await call_next()
    await asyncio.sleep(0.01)
    ctx['call_log'].append(f"async_middleware2_exit with {type(result).__name__}")
    await asyncio.sleep(0.01)
    return f"2:{result}:2"

    
def sync_handler(text, call_log):
    call_log.append("sync_handler")
    return text.upper()


async def async_handler(text, call_log):
    call_log.append("async_handler")
    return text.upper()


async def run(use_async_context_manager, use_call_async, ctx, handler_fn):
    if use_async_context_manager:
        async with ctx:
            if use_call_async:
                result = await ctx.call_async(handler_fn, "foo")
            else:
                result = ctx.call(handler_fn, "foo")

    else:
        with ctx:
            if use_call_async:
                result = await ctx.call_async(handler_fn, "foo")
            else:
                result = ctx.call(handler_fn, "foo")
    return result


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "use_async_context_manager, use_call_async, enter_type, exit_type, middleware1_type, middleware2_type, handler_type",
    list(
        itertools.product(
        [True, False], 
        [True, False],
        ["sync", "async"],  # Enter hook types
        ["sync", "async"],  # Exit hook types
        ["sync", "async"],  # Middleware 1 types
        ["sync", "async"],  # Middleware 2 types
        ["sync", "async"],  # Handler types
    ))
)
async def test_transaction_context_async(use_async_context_manager, use_call_async, enter_type, exit_type, 
                                         middleware1_type, middleware2_type, handler_type):
    call_log = []
    ctx = TransactionContext(call_log=call_log)
    ctx.configure(
        on_enter_transaction_context=enter_hook_fn if enter_type == "sync" else async_enter_hook_fn,
        on_exit_transaction_context=exit_hook_fn if exit_type == "sync" else async_exit_hook_fn,
        middlewares=[
            middleware1_fn if middleware1_type == "sync" else async_middleware1_fn,
            middleware2_fn if middleware2_type == "sync" else async_middleware2_fn,
        ]
    )
    use_async_context_manager = any(x == "async" for x in [enter_type, exit_type, middleware1_type, middleware2_type, handler_type])

    handler_fn = sync_handler if handler_type == "sync" else async_handler

    should_raise_exception = any([
        (middleware1_type == "async" or middleware2_type == "async") and not use_call_async, # using call_async is required with async middleware
        middleware2_type == "sync" and handler_type == "async", # using sync middleware with async handler is forbidden
        middleware1_type == "sync" and middleware2_type == "async", # using sync middleware with async call_next is forbidden
    ])

    if should_raise_exception:
        with pytest.raises(TypeError):
            await run(use_async_context_manager, use_call_async, ctx, handler_fn)
    else:
        result = await run(use_async_context_manager, use_call_async, ctx, handler_fn)
        
        assert result == "1:2:FOO:2:1"
        assert call_log == [
            f"{enter_type}_enter",
            f"{middleware1_type}_middleware1_enter",
            f"{middleware2_type}_middleware2_enter",
            f"{handler_type}_handler",
            f"{middleware2_type}_middleware2_exit with str",
            f"{middleware1_type}_middleware1_exit with str",
            f"{exit_type}_exit"
        ]
        
    
    