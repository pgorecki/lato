import io

from lato import Application

from .employee_module import employee_module
from .project_module import project_module


class Logger:
    def __init__(self):
        self.history = []

    def printlog(self, *args, **kwargs):
        output = io.StringIO()
        print(*args, file=output, end="", **kwargs)
        contents = output.getvalue()
        output.close()
        self.history.append(contents)
        print(*args, **kwargs)


def create_app():
    logger = Logger()

    app = Application("Modular Application", logger=logger, printlog=logger.printlog)
    app.include_submodule(project_module)
    app.include_submodule(employee_module)

    @app.on_enter_transaction_context
    def on_enter_transaction_context(ctx):
        printlog = ctx[Logger].printlog
        ctx.dependency_provider.update(emit=ctx.emit)
        printlog("Entering transaction")

    @app.on_exit_transaction_context
    def on_exit_transaction_context(ctx, exception):
        printlog = ctx[Logger].printlog
        if exception:
            printlog("Rolling back due to", exception)
        else:
            printlog("Committing transaction")

    # @app.transaction_middleware
    # def useless_middleware(ctx, call_next):
    #     printlog = ctx[Logger].printlog
    #     printlog("before call")
    #     result = call_next()
    #     printlog("after call")
    #     return result

    return app
