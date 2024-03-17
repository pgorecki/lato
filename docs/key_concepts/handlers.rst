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
        print("called directly")

    app = Application("example")
    
    app.call(foo)

And the output is: 

.. testoutput::

    called


Calling a function using an *alias*
-----------------------------------

In this approach, a function is first decorated with :func:`ApplicationM.handler`, and then called using an alias:

.. testcode::
    from lato import ApplicationModule

    from lato import Application
    app = Application("example")

    @app.handler("alias_of_foo")
    def foo():
        print("called via alias")
 
    app.call("alias_of_foo")

And the output is: 

.. testoutput::

    called via alias


Calling the function using a message handler
--------------------------------------------

In this approach, a message is declared, then a :func:`Application.handler` decorator is used to 
associate the message with its handler.