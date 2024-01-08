from lato import Application, ApplicationModule, Event


class SampleEvent(Event):
    ...


def create_app(**kwargs):
    app = Application(name="App", **kwargs)

    module_a = ApplicationModule("Module A")
    module_b = ApplicationModule("Module B")
    module_c = ApplicationModule("Module C")

    app.include_submodule(module_a)
    app.include_submodule(module_b)

    module_b.include_submodule(module_c)

    @module_a.on(SampleEvent)
    def on_sample_event_a(event: SampleEvent, buffer):
        buffer.append("a")

    @module_b.on(SampleEvent)
    def on_sample_event_b(event: SampleEvent, buffer):
        buffer.append("b")

    @module_c.on(SampleEvent)
    def on_sample_event_b(event: SampleEvent, buffer):
        buffer.append("c")

    return app


def test_emit_events():
    buffer = []
    app = create_app(buffer=buffer)

    event = SampleEvent()
    app.emit(event)

    assert len(app.get_handlers_for(SampleEvent)) == 3
    assert buffer == ["a", "b", "c"]
