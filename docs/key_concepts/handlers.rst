Message Handlers
================

There are 3 way of interacting with lato application. 

1. Directly invoking a function,
2. Calling a function using an *alias*,
3. Calling the function using a message handler.

Let's have a closer look at all the possibilities.

Directly invoking a function
----------------------------

In this approach, a function is passed to a :func:`Application.call` as is:

.. testcode::

    from lato import Application

    def foo():
        return "called directly"

    app = Application("example")
    
    assert app.call(foo) == "called directly"


Calling a function using an *alias*
-----------------------------------

In this approach, a function is first decorated with :func:`ApplicationM.handler`, and then called using an alias:

.. testcode::

    from lato import Application
    app = Application("example")

    @app.handler("alias_of_bar")
    def bar():
        return "called via alias"
 
    app.call("alias_of_bar") == "called via alias"


Calling the function using a command
--------------------------------------------

In this approach, a command is declared, then a :func:`Application.handler` decorator is used to 
associate the command with its handler.

.. testcode::

    from lato import Application, Command
    app = Application("example")

    class SampleCommand(Command):
        x: int


    @app.handler(SampleCommand)
    def sample_command_handler(command: SampleCommand):
        return f"called sample command with x={command.x}"
 
    app.execute(SampleCommand(x=1)) == "called sample command with x=1"