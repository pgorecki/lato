Transaction callbacks and middlewares
=====================================

In most cases, the handler is executed by calling one of the Application methods: :func:`~lato.Application.call`, 
:func:`~lato.Application.execute`, or :func:`~lato.Application.publish`, which creates the transaction context under the
hood. 

When :func:`~lato.Application.call` or similar method is executed, the lifecycle of handler execution is as following:

1. ``on_enter_transaction_context`` callback is invoked

2. ``transaction_middleware`` functions, wrapping the handler are invoked

3. handler function is invoked 

4. ``on_exit_transaction_context`` callback is invoked

The application can be configured to use any of the callbacks by using decorators:

.. testcode::

    from typing import Optional, Callable
    from lato import Application, TransactionContext
    

    app = Application()

    @app.on_enter_transaction_context
    def on_enter_transaction_context(ctx: TransactionContext):
        print("starting transaction")

    @app.on_exit_transaction_context
    def on_exit_transaction_context(ctx: TransactionContext, 
                                    exception: Optional[Exception]=None):
        print("exiting transaction context")

    @app.transaction_middleware
    def middleware1(ctx: TransactionContext, call_next: Callable):
        print("entering middleware1")
        result = call_next()  # will call middleware2
        print("exiting middleware1")
        return result

    @app.transaction_middleware
    def middleware2(ctx: TransactionContext, call_next: Callable):
        print("entering middleware2")
        result = call_next()  # will call the handler
        print("exiting middleware2")
        return f"[{result}]"

    def to_uppercase(s):
        print("calling handler")
        return s.upper()

    
    print(app.call(to_uppercase, "foo"))

This will generate the output:

.. testoutput::

    starting transaction
    entering middleware1
    entering middleware2
    calling handler
    exiting middleware2
    exiting middleware1
    exiting transaction context
    [FOO]

Any of the callbacks is optional, and there can be multiple ``transaction_middleware`` callbacks.
``on_enter_transaction_context`` is a good place to set up the transaction level dependencies, i.e. the dependencies
that change with every transaction - correlation id, current time, database session, etc. ``call_next`` is a ``functools.partial`` object,
so you can inspect is arguments using ``call_next.args`` and ``call_next.keywords``.
