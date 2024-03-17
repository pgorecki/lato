import asyncio
import logging

from lato import Application, TransactionContext

logging.basicConfig(level=logging.INFO)
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
