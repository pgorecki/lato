.. _dependency_injection:


Dependency Injection
====================

:func:`~lato.DependencyProvider` is an interface for any concrete provider capable of resolving and matching function 
parameters. Both :func:`~lato.Application` and :func:`~lato.TransactionContext` internally use dependency provider 
to resolve handler parameters. By default use dict based implementation
:func:`~lato.dependency_provider.BasicDependencyProvider`. 


This code demonstrates basic functionality of a dependency provider

.. testcode::

    from lato.dependency_provider import BasicDependencyProvider

    class FooService():
        pass

    def a_handler(service: FooService):
        pass

    foo_service = FooService()
    dp = BasicDependencyProvider(foo_service=foo_service)
    assert dp[FooService] is foo_service
    assert dp["foo_service"] is foo_service

    assert dp.resolve_func_params(a_handler) == {'service': foo_service}

``lagom`` integration
---------------------

This code showcases a dependency provider based on ``lagom``:

.. literalinclude:: ../../examples/example3/lagom_integration.py


``dependency_injector`` integration
-----------------------------------

This code showcases a dependency provider based on ``dependency_injector``:

.. literalinclude:: ../../examples/example3/dependency_injector_integration.py
