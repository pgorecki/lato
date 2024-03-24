Events and publish-subscribe
============================

Application modules can interact by publishing and subscribing to messages. Events can be published
using a ``TransactionContext``, and received by an event handler. There can be multiple handlers bound to
a single event. If the application is receiving an event from an external source, 
it should be processed using ``Application.publish()``:


.. testcode::
    
    from lato import Application, ApplicationModule, Event, Command, TransactionContext

    class SampleCommand(Command):
        pass

    class FooHappened(Event):
        source: str

    foo_module = ApplicationModule(name="foo")
    @foo_module.handler(SampleCommand)
    def call_foo(command: SampleCommand, ctx: TransactionContext):
        print("handling foo")
        ctx.publish(FooHappened(source="foo"))

    bar_module = ApplicationModule(name="bar")
    @bar_module.handler(FooHappened)
    def on_foo_happened(event: FooHappened):
        print(f"handling event from {event.source}")

    foobar = Application()
    foobar.include_submodule(foo_module)
    foobar.include_submodule(bar_module)

    foobar.execute(SampleCommand())
    foobar.publish(FooHappened(source="external source"))

And the output is:

.. testoutput::
    
    handling foo
    handling event from foo
    handling event from external source