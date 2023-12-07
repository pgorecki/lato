from lato import Application, ApplicationModule, Task
from lato.compositon import compose


def test_composition():
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
