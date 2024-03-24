import pytest

from lato import Application, Command, Event, TransactionContext


class FooService:
    ...


def test_app_transaction_context():
    foo_service = FooService()
    app = Application(foo_service=foo_service)
    ctx = app.transaction_context()

    assert ctx.dependency_provider is not app.dependency_provider
    assert foo_service is ctx[FooService] is app[FooService]


def test_app_transaction_context_with_kwargs():
    foo_service = FooService()
    app = Application(foo_service=foo_service)
    ctx = app.transaction_context(x=1)

    assert ctx.dependency_provider is not app.dependency_provider
    assert (
        foo_service
        is ctx.dependency_provider[FooService]
        is app.dependency_provider[FooService]
    )
    assert ctx.dependency_provider["x"] == 1


def test_app_enter_exit_transaction_context():
    app = Application()

    @app.on_enter_transaction_context
    def on_enter_transaction_context(ctx):
        ctx.entered = True

    @app.on_exit_transaction_context
    def on_exit_transaction_context(ctx, exception=None):
        ctx.exited = True

    with app.transaction_context() as ctx:
        ...

    assert ctx.entered
    assert ctx.exited


def test_app_call():
    app = Application()

    def add(x, y):
        return x + y

    assert app.call(add, 10, 1) == 11


def test_app_call_by_alias():
    app = Application()

    @app.handler("add")
    def add(x, y):
        return x + y

    assert app.call("add", 10, 1) == 11


def test_app_exception_within_call():
    app = Application()

    @app.on_enter_transaction_context
    def on_enter_transaction_context(ctx):
        ctx.entered = True

    @app.on_exit_transaction_context
    def on_exit_transaction_context(ctx, exception=None):
        if exception:
            ctx.exception = exception

    def foo():
        raise ValueError()

    with pytest.raises(ValueError) as exc:
        with app.transaction_context() as ctx:
            ctx.call(foo)

        assert ctx.entered
        assert ctx.exception is exc


def test_app_uses_middleware():
    app = Application()

    @app.transaction_middleware
    def middleware1(ctx, call_next):
        ctx["buffer"].append(1)
        return call_next()

    @app.transaction_middleware
    def middleware2(ctx, call_next):
        ctx["buffer"].append(2)
        result = call_next()
        ctx["buffer"].append(4)
        return result

    def foo(ctx: TransactionContext):
        ctx["buffer"].append(3)
        return "ok"

    with app.transaction_context(buffer=[]) as ctx:
        result = ctx.call(foo)

    assert ctx["buffer"] == [1, 2, 3, 4]
    assert result == "ok"


def test_emitting_and_handling_events():
    app = Application()

    @app.handler("sample_event")
    def on_sample_event(x, buffer):
        buffer.append(f"on_sample_event {x}")

    def sample_use_case(ctx, buffer):
        buffer.append("begin sample_use_case")
        ctx.emit("sample_event", "foo")
        buffer.append("end sample_use_case")

    with app.transaction_context(buffer=[]) as ctx:
        ctx.call(sample_use_case)

    assert ctx["buffer"] == [
        "begin sample_use_case",
        "on_sample_event foo",
        "end sample_use_case",
    ]


def test_emitting_and_handling_events_uses_middleware():
    app = Application()

    class Counter:
        def __init__(self):
            self.value = 0

        def inc(self):
            self.value += 1

    @app.transaction_middleware
    def sample_middleware(ctx, call_next):
        ctx[Counter].inc()
        call_next()

    @app.handler("sample_event")
    def on_sample_event():
        ...

    def sample_use_case(ctx):
        ctx.emit("sample_event", "foo")

    with app.transaction_context(counter=Counter()) as ctx:
        ctx.call(sample_use_case)

    assert ctx[Counter].value == 2


def test_app_executes_command():
    app = Application()

    class MyCommand(Command):
        message: str

    @app.handler(MyCommand)
    def handle_my_command(command: MyCommand):
        return f"processed {command.message}"

    command = MyCommand(message="foo")
    assert app.execute(command) == "processed foo"


def test_app_handles_external_event():
    app = Application()

    class MyEvent(Event):
        message: str

    @app.handler(MyEvent)
    def handle_my_event(event: MyEvent):
        return f"handled {task.message}"

    task = MyEvent(message="foo")
    assert tuple(app.publish(task).values()) == ("handled foo",)


def test_create_transaction_context_callback():
    from lato import Application, TransactionContext

    app = Application()

    class CustomTransactionContext(TransactionContext):
        pass

    @app.on_create_transaction_context
    def create_transaction_context(**kwargs):
        return CustomTransactionContext(**kwargs)

    ctx = app.transaction_context(foo="bar")
    assert isinstance(ctx, CustomTransactionContext)
