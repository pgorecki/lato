.. _transaction_context:

Transaction Context
===================

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

