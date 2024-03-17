import asyncio

from lato import Application, TransactionContext


async def add_async(a, b):
    await asyncio.sleep(1)
    return a + b


if __name__ == "__main__":
    with TransactionContext() as ctx:
        result = ctx.call(add_async, 1, 2)
        print(result)

    result = asyncio.run(result)

    print("got result from asyncio.run", result)

    app = Application("async")
    result = app.call(add_async, 1, 2)
    print(result)
