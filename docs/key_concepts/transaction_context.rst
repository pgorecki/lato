.. _transaction_context:

Transaction Context
===================

:func:`~lato.TransactionContext` is a core building block in ``lato``. It's main purpose is to inject dependencies into a handler function.
When ``TransactionContext`` is calling a function using `call` method, it will inspect all its arguments and 
it will try to inject all matching dependencies into it. This greatly simplifies testing.

You can instantiate :func:`~lato.TransactionContext` with any args and kwargs. These arguments will be injected to a handler 
during a call. Any arguments passed to ``TransactionContext.call`` that match the function 
signature will be passed to the called function, and will replace the ones passed in the constructor.

::

    from lato import TransactionContext 

    def greet(name, greeting):
        return f"{greeting}, {name}!"

    ctx = TransactionContext()
    result = ctx.call(greet, greeting="Hello", name="Alice")
    
    assert result == "Hello, Alice!"

As you can see, ``greeting`` and ``name`` arguments in ``TransactionContext.call()`` are actually passed to the ``greet`` function.
You can use both keyword and positional arguments::
    
    ctx.call(greet, "Alice", "Hello")
    ctx.call(greet, "Alice", greeting="Hello")
    

Instead of passing passing dependencies to ``TransactionContext.call()``, it's often more convenient to pass them to ``TransactionContext`` 
constructor::

    from lato import TransactionContext 

    def greet(name, greeting):
        return f"{greeting}, {name}!"

    ctx = TransactionContext(greeting="Hola")
    print(ctx.call(greet, "Bob"))
    print(ctx.call(greet, "Charlie"))

.. note::
    Any arguments passed to ``TransactionContext.call()`` will override arguments passed to the TransactionContext constructor.

::

    class FooService:
        ...

    def do_something(foo_service):
        ...

    def do_something_else(service: FooService):
        ...

    ctx = TransactionContext(foo_service=FooService())
    ctx.call(do_something)  # will inject an instance of FooService using name `foo_service`  
    ctx.call(do_something_else)  # will inject an instance of FooService using type `FooService`


``TransactionContext`` is also a context manager, so you can use it with ``with`` statement::

    from lato import TransactionContext 

    def greet(name, greeting):
        return f"{greeting}, {name}!"

    with TransactionContext(greeting="Hola") as ctx:
        print(ctx.call(greet, "Bob"))
        print(ctx.call(greet, "Charlie"))



It is rarely needed to instantiate transaction context directly. In most cases, it is sufficient to call 
any of the Application methods: :func:`~lato.Application.call`, 
:func:`~lato.Application.execute`, or :func:`~lato.Application.publish`, which creates the transaction context under the
hood.