import asyncio

from lato import Application, Command


class MultiplyCommand(Command):
    a: int
    b: int


app = Application("async")


@app.handler(MultiplyCommand)
async def multiply_async(command: MultiplyCommand):
    await asyncio.sleep(1)
    return command.a * command.b


coroutine = app.execute(MultiplyCommand(a=10, b=20))
print("execution result", coroutine)
