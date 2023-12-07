 .. lato documentation master file, created by
   sphinx-quickstart on Fri Oct 27 18:16:19 2023.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to lato's documentation!
================================



..  toctree::
    :maxdepth: 2
    :caption: Contents:
    
    dependency_provider


``lato`` is a microframework for building modular applications in Python. It helps you to build applications 
that are easy to maintain and extend. It is based on the idea of `modularity <https://en.wikipedia.org/wiki/Modular_programming>`_ 
and `dependency injection <https://en.wikipedia.org/wiki/Dependency_injection>`_.

If you are trying to build a modular monolith, ``lato`` is the right choice for you. It is framework agnostic,
you can use it with any framework you want (`Flask`, `FastAPI`, ...).


Installation
============

``lato`` is available on `PyPI <https://pypi.org/project/lato/>`_ and can be installed with pip::

    pip install lato

Basic Concepts
==============

``TransactionContext`` is a core concept of ``lato``. It's main purpose is to inject dependencies into any function.
When ``TransactionContext`` is calling a function using `call` method, it will inspect all its arguments and 
it will try to inject its arguments (dependencies) into it. Any arguments passed to ``TransactionContext.call`` that 
match to the function signature will be passed to the called function.

::

    from lato import TransactionContext 

    def greet(name, greeting):
        return f"{greeting}, {name}!"

    ctx = TransactionContext()
    result = ctx.call(greet, greeting="Hello", name="Alice")
    
    assert result == "Hello, Alice!"

As you can see, ``greeting`` and ``name`` arguments in ``TransactionContext.call`` are actually passed to the ``greet`` function.
You can use both keyword and positional arguments::
    
    ctx.call(greet, "Alice", "Hello")
    ctx.call(greet, "Alice", greeting="Hello")
    

Instead of passing passing dependencies to ``TransactionContext.call``, it's often more convenient to pass them to ``TransactionContext`` 
constructor::

    from lato import TransactionContext 

    def greet(name, greeting):
        return f"{greeting}, {name}!"

    ctx = TransactionContext(greeting="Hola")
    print(ctx.call(greet, "Bob"))
    print(ctx.call(greet, "Charlie"))

.. note::
    Any arguments passed to ``TransactionContext.call`` will override arguments passed to the constructor.


``TransactionContext`` is capable of injecting positional arguments, keyworded arguments, and typed arguments.

::

    class FooService:
        ...

    def do_something(foo_service):
        ...

    def do_something_else(service: FooService):
        ...

    ctx = TransactionContext(foo_service=FooService())
    ctx.call(do_something)
    ctx.call(do_something_else)





``TransactionContext`` is also a context manager, so you can use it with ``with`` statement::

    from lato import TransactionContext 

    def greet(name, greeting):
        return f"{greeting}, {name}!"

    with TransactionContext(greeting="Hola") as ctx:
        print(ctx.call(greet, "Bob"))
        print(ctx.call(greet, "Charlie"))

``TransactionContext`` is also a decorator, so you can use it to decorate any function::

    from lato import TransactionContext 

    @TransactionContext(greeting="Hola")
    def greet(name, greeting):
        return f"{greeting}, {name}!"

    print(greet("Bob"))
    print(greet("Charlie"))

``TransactionContext`` is also a class, so you can inherit from it::

    from lato import TransactionContext 

    class MyTransactionContext(TransactionContext):
        def __init__(self, greeting, **kwargs):
            super().__init__(**kwargs)
            self.greeting = greeting

        def greet(self, name):
            return f"{self.greeting}, {name}!"

    ctx = MyTransactionContext(greeting="Hola")
    print(ctx.greet("Bob"))
    print(ctx.greet("Charlie"))

``TransactionContext`` is also a context manager, so you can use it with ``with`` statement::

    from lato import TransactionContext 

    class MyTransactionContext(TransactionContext):
        def __init__(self, greeting, **kwargs):
            super().__init__(**kwargs)
            self.greeting = greeting

        def greet(self, name):
            return f"{self.greeting}, {name}!"

    with MyTransactionContext(greeting="Hola") as ctx:
        print(ctx.greet("Bob"))
        print(ctx.greet("Charlie"))

``TransactionContext`` is also a decorator, so you can use it to decorate any function::

    from lato import TransactionContext 

    class MyTransactionContext(TransactionContext):
        def __init__(self, greeting, **kwargs):
            super().__init__(**kwargs)
            self.greeting = greeting

        def greet(self, name):
            return f"{self.greeting}, {name}!"

    @MyTransactionContext(greeting="Hola")
    def greet(name, greeting):
        return f"{greeting}, {name}!"

    print(greet("Bob"))
    print

.. testcode::

   1+1         # this will give no output!
   print(2+2)  # this will give output

.. testoutput::

   4

.. If you are new to `lato`, you should start with the :ref:`dependency_provider`.

Test
==================

.. autofunction:: lato.as_type

.. autoclass:: lato.DependencyProvider
   :members:

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`



zzzzzz
======

Cookbook

Crawl a web page

The most simple way to use our program is with no arguments.
Simply run:

python main.py -u <url>

to crawl a webpage.

Crawl a page slowly

To add a delay to your crawler,
use -d:

python main.py -d 10 -u <url>

This will wait 10 seconds between page fetches.

Crawl only your blog

You will want to use the -i flag,
which while ignore URLs matching the passed regex::

python main.py -i "^blog" -u <url>

This will only crawl pages that contain your blog URL.
