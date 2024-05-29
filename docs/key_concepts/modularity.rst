Modularity
==========

Breaking down applications into separate, self-contained modules that represent distinct bounded contexts is a 
common practice. These modules encapsulate cohesive components such as entities, repositories, and services, 
ensuring that each part of the application remains focused on its specific functionality and responsibilities. 
This modular approach facilitates maintainability, scalability and reusability by drawing clear boundaries 
between different parts of the system.

Basics
------

In *lato*, *Application* can be decomposed into *ApplicationModules* like so:

.. testcode::
    
    from lato import Application, ApplicationModule

    foo_module = ApplicationModule(name="foo")
    @foo_module.handler("foo")
    def call_foo():
        print("foo")

    bar_module = ApplicationModule(name="bar")
    @bar_module.handler("bar")
    def call_bar():
        print("bar")

    foobar = Application()
    foobar.include_submodule(foo_module)
    foobar.include_submodule(bar_module)

    foobar.call("foo")
    foobar.call("bar")

.. testoutput::
    
    foo
    bar

Application modules can create hierarchies, i. e. top level module can be further composed into submodules if needed.

Application module structure
----------------------------

The application module can be implemented as a Python package::

    src/
    ├── application.py
    └── sample_module/
       ├── __init__.py
       ├── commands.py
       └── events.py

..  code-block:: python

    # sample_module/__init__.py
    import importlib
    from lato import ApplicationModule
    
    a_module = ApplicationModule("sample")
    importlib.import_module("sample_module.commands")
    importlib.import_module("sample_module.events")

..  code-block:: python

    # sample_module/commands.py
    from lato import Command
    from sample_module import a_module
    
    class SampleCommand(Command):
        pass
    
    @a_module.handler(SampleCommand)
    def handle_sample_command(command: SampleCommand):
        pass

..  code-block:: python

    # sample_module/events.py
    from lato import Event
    from sample_module import a_module
    
    class SampleEvent(Event):
        pass
    
    @a_module.handler(SampleEvent)
    def on_sample_event(event: SampleEvent):
        pass

..  code-block:: python

    # application.py
    from lato import Application
    from sample_module import a_module
    from sample_module.co
    
    app = Application()
    app.include_submodule(a_module)
    
    @a_module.handler(SampleEvent)
    def on_sample_event(event: SampleEvent):
        pass

