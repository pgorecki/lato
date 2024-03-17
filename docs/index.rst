.. meta::
   :http-equiv=Content-Type: text/html; charset=ISO-8859-1

Lato documentation
==================

**Lato** is a microframework for building modular applications in Python. It helps you to build applications 
that are easy to maintain and extend. It is based on such concepts as 
`modularity <https://en.wikipedia.org/wiki/Modular_programming>`_,
`dependency injection <https://en.wikipedia.org/wiki/Dependency_injection>`_, 
and `loose coupling <https://en.m.wikipedia.org/wiki/Loose_coupling>`_.

If you are trying to build a modular monolith in Python, **Lato** is the right choice for you. It is framework agnostic,
you can use it with any framework of your choice, i.e. `Flask`, `FastAPI`, etc.

Lato is Open Source and licensed under the MIT License.


Core Features
-------------

- **Modularity**: Organize your application into smaller, independent modules for better maintainability.

- **Flexibility**: Loosely couple your application components, making them easier to refactor and extend.

- **Testability**: Easily test your application components in isolation.

- **Minimalistic**: Intuitive and lean API for rapid development without the bloat.

Contents
--------

..  toctree::
    :maxdepth: 2

    tutorial/index
    key_concepts/index
    concurrency
    testing
    api

Installation
============

**Lato** is available on `PyPI <https://pypi.org/project/lato/>`_ and can be installed with pip::

    pip install lato

Getting Started
===============

The ``Application`` serves as a top-level building block in **Lato**. 
Let's create a simple greeting application. When you instantiate the application
you need to name it, and in addition you can pass as many keyword arguments as you need - they will be used as dependencies. 
Later on you will see how the dependencies are being used. 

Let's create the application with one dependency - ``greeting_phrase``:


.. testcode::
    
    from lato import Application

    app = Application(name="Hello World", greeting_phrase="Hello")


Resolving parameters
--------------------

Now, let's see the core feature of **Lato** - *automatic parameter resolution*.
To demonstrate it, let's declare a ``greet_person`` function and invoke it via ``app.call``:

.. testcode::

    def greet_person(person: str, greeting_phrase: str):
        return f"{greeting_phrase} {person}"

    result = app.call(greet_person, "Bob")

    assert result == "Hello Bob"

The ``greet_person`` function requires two arguments: ``person`` and ``greeting phrase``. When invoking the function via ``Application.call()``, 
we provided only one argument - the value of ``person``. The other argument - ``greeting phrase`` is automatically 
provided (injected) by the app, as you provided it as a dependency. In general, **Lato** application is capable of injecting 
missing function arguments, if the function parameter matches the dependency (either by parameter name, or by type).


Declaring a handler
-------------------

To understand what a handler is, think of it as of named function. This name is an *alias*, which is a string.
When invoking a handler, you can pass an alias instead of the function itself. This idea promotes loose coupling.

You can create the handler and call it using its alias like so:

.. testcode::

    @app.handler("greet")
    def greet_person(person: str, greeting_phrase: str):
        return f"{greeting_phrase} {person}"

    result = app.call("greet", "Bob")
    assert result == "Hello Bob"

 
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

Instead of using an alias, you can create a command handler, and then invoke the handler by calling ``App.execute()``:

.. testcode::
    
    from lato import Command
    
    class Greet(Command):
        title: str        
        name: str

    @app.handler(Greet)
    def greet_person(command: Greet, greeting_phrase: str):
        return f"{greeting_phrase} {command.title} {command.name}"

    result = app.execute(Greet(title="Mr", name="Bob"))
    assert result == "Hello Mr Bob"

The ``Application.execute()`` passes the command to a designated handler. It should be noted that the first parameter 
of a command handler is a command, and the remaining parameters are resolved from application dependencies.

Integration with a web framework
--------------------------------

**Lato** is web framework agnostic. Let's see how it fits into our framework of choice - FastAPI:

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
