from lato import Application, ApplicationModule, Task
from lato.compositon import compose


class SampleQuery(Task):
    ...


def create_app(**kwargs):
    app = Application(name="App", **kwargs)

    module_a = ApplicationModule("Module A")
    module_b = ApplicationModule("Module B")
    module_c = ApplicationModule("Module C")

    app.include_submodule(module_a)
    app.include_submodule(module_b)

    module_b.include_submodule(module_c)

    @module_a.handler(SampleQuery)
    def on_query_a(query: SampleQuery):
        return dict(a="foo")

    @module_b.handler(SampleQuery)
    def on_query_b(query: SampleQuery):
        return dict(b="bar")

    @module_c.handler(SampleQuery)
    def on_query_c(query: SampleQuery):
        return dict(c="baz")

    return app


def test_manual_composition():
    class SampleTask(Task):
        ...

    module1 = ApplicationModule("module1")

    @module1.handler(SampleTask)
    def module1_handler(task: SampleTask):
        return dict(module1="foo")

    module2 = ApplicationModule("module2")

    @module2.handler(SampleTask)
    def module2_handler(task: SampleTask):
        return dict(module2="bar")

    app = Application("app")
    app.include_submodule(module1)
    app.include_submodule(module2)

    result = app.execute(SampleTask())
    assert result == ({"module1": "foo"}, {"module2": "bar"})

    result = compose(app.execute(SampleTask()))
    assert result == {"module1": "foo", "module2": "bar"}


def test_query_composition():
    app = create_app()
    result = app.query(SampleQuery())

    # assert
    assert result == {
        "a": "foo",
        "b": "bar",
        "c": "baz"
    }


def test_compose_decorator():
    # arrange
    app = create_app()

    @app.compose(SampleQuery)
    def compose_sample_query(result):
        # this function will receive a tuple of results from all 3 handlers
        result = compose(result)
        return result["a"] + result["b"] + result["c"]

    # act
    result = app.query(SampleQuery())

    # assert
    assert result == "foobarbaz"
