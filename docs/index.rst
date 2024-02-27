Welcome to lato documentation!
==============================


..  toctree::
    :maxdepth: 3

    tutorial/index
    key_concepts/index
    testing
    api


**Lato** is a microframework for building modular applications in Python. It helps you to build applications 
that are easy to maintain and extend. It is based on the idea of `modularity <https://en.wikipedia.org/wiki/Modular_programming>`_ 
and `dependency injection <https://en.wikipedia.org/wiki/Dependency_injection>`_.

If you are trying to build a modular monolith, **Lato** is the right choice for you. It is framework agnostic,
you can use it with any framework you want (`Flask`, `FastAPI`, ...).

Features:

- CQRS
- dependency injection


Installation
============

**Lato** is available on `PyPI <https://pypi.org/project/lato/>`_ and can be installed with pip::

    pip install lato

Getting Started
===============

The ``Application`` serves as a top-level building block in **Lato**. 
Let's create a useless greeting application. During the construction of the application,
we can pass as many dependencies as we need - and later on we will see how the dependencies are being used. 
In this example we will need only one dependency: ``greeting_phrase``:


.. testcode::
    
    from lato import Application

    app = Application(name="Hello World", greeting_phrase="Hello")


Resolving parameters
--------------------

Now, let's see the core feature of **Lato** - *automatic parameter resolution*.
To demonstrate it, we will declare a ``greet_person`` function and call it via ``app``:

.. testcode::

    def greet_person(person: str, greeting_phrase: str):
        return f"{greeting_phrase} {person}"

    result = app.call(greet_person, "Bob")

    assert result == "Hello Bob"

The ``greet_person`` function requires two arguments: ``person`` and ``greeting phrase``. When invoking the function via ``Application.call()``, 
we provided only one argument - the value for ``person``. The missing ``greeting phrase`` argument was automatically 
provided (injected) by the app, as it was declared as a dependency earlier. In general, **Lato** is capable of resolving 
missing arguments both by name and by type.


Declaring a handler
-------------------

To understand what a handler is, think of it as an entry point or a use case that your application implements.

Now, let's decorate the ``greet_person`` function with an alias:

.. testcode::

    @app.handler("greet")
    def greet_person(person: str, greeting_phrase: str):
        return f"{greeting_phrase} {person}"

    result = app.call("greet", "Bob")
    assert result == "Hello Bob"

When invoking a handler, you can pass an alias instead of the actual function object. 
You could use this behavior in a simple command line tool, like so:

..  code-block:: python

    if __name__ == "__main__":
        command = sys.argv[1]
        name = sys.argv[2]
        print(app.call(command, name))


Using a command handler
-----------------------

**Lato** follows the `Command Pattern <https://en.wikipedia.org/wiki/Command_pattern>`_ in its design. 
It is a behavioral design pattern which is used to implement lose coupling in a request-response model.
The idea is to turn a request (command) into a standalone object. This object contains all parameters that are required 
to handle a request. Such separation allows for queuing of requests, logging of the parameters for better observability,
and invocation of the request.

Let's see how we can declare our function as a command handler:

.. testcode::
    
    from lato import Task as Command
    
    class Greet(Command):
        title: str        
        name: str

    @app.handler(Greet)
    def greet_person(command: Greet, greeting_phrase: str):
        return f"{greeting_phrase} {command.title} {command.name}"

    result = app.execute(Greet(title="Mr", name="Bob"))
    assert result == "Hello Mr Bob"

The ``Application.execute()`` passes the command to a designated handler. It should be noted that the first parameter 
of a command handler must be a command, and the remaining parameters are resolved as dependencies.

Integration with a web framework
--------------------------------

Let's see how **Lato** fits into frameworks.

..  code-block:: python

    from fastapi import FastAPI
    from lato import Application, Command
    
    app = Application("Greetings", greeting_phrase="Hello")
    
    class Greet(Command):
        title: str        
        name: str

    @app.handler(Greet)
    def greet_person(command: Greet, greeting_phrase: str):
        return f"{greeting_phrase} {task.title} {task.name}"


    api = FastAPI()
    @api.get("/greet")
    def foo(request, title: str, name: str):
        command = Greet(title, name)
        message = app.execute(command)
        return {'message': message}
