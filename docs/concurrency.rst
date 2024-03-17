.. _concurrency:

Concurrency
===========

Lato supports ``async / await`` syntax. To make your synchronous code *asynchronous* simply replace:

- ``app.call()`` with ``app.call_async()``
- ``app.execute()`` with ``app.execute_async()``
- ``app.publish()`` with ``app.publish_async()``

Below is an example of async application:

.. testcode::

    import asyncio
    import logging
    
    from lato import Application, TransactionContext
    
    logging.basicConfig(level=logging.DEBUG)
    root_logger = logging.getLogger("toy")
    
    app = Application()
    
    
    class Counter:
        def __init__(self):
            self.value = 0
    
        def next(self):
            self.value += 1
            return self.value
    
    
    counter = Counter()
    
    
    @app.on_enter_transaction_context
    async def on_enter_transaction_context(ctx: TransactionContext):
        correlation_id = str(counter.next())
        logger = root_logger.getChild(correlation_id)
        ctx.set_dependencies(logger=logger)
        logger.info("Connecting to database")
        await asyncio.sleep(0.001)
        logger.info("Connected")
    
    
    @app.on_exit_transaction_context
    async def on_exit_transaction_context(ctx: TransactionContext, exception=None):
        logger = ctx["logger"]
        logger.info("Disconnecting from database")
        await asyncio.sleep(0.001)
        logger.info("Disconnected from database")
    
    
    @app.handler("foo")
    async def handle_foo(x, logger):
        logger.info(f"Starting foo, x={x}")
        await asyncio.sleep(0.001)
        logger.info("Finished foo")
    
    
    async def main() -> None:
        await asyncio.gather(
            app.call_async("foo", x=1),
            app.call_async("foo", x=2),
            app.call_async("foo", x=3),
        )
    
    
    asyncio.run(main())


And the output is: 

.. testoutput::

    INFO:toy.1:Connecting to database
    INFO:toy.2:Connecting to database
    INFO:toy.3:Connecting to database
    INFO:toy.1:Connected
    INFO:toy.1:Starting foo, x=1
    INFO:toy.2:Connected
    INFO:toy.2:Starting foo, x=2
    INFO:toy.3:Connected
    INFO:toy.3:Starting foo, x=3
    INFO:toy.1:Finished foo
    INFO:toy.1:Disconnecting from database
    INFO:toy.2:Finished foo
    INFO:toy.2:Disconnecting from database
    INFO:toy.3:Finished foo
    INFO:toy.3:Disconnecting from database
    INFO:toy.1:Disconnected from database
    INFO:toy.2:Disconnected from database
    INFO:toy.3:Disconnected from database


Feel free to check other example in the repository: https://github.com/pgorecki/lato/tree/main/examples/async_example