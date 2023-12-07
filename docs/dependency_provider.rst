Dependency Provider
===================

..  _dependency_provider:

Basic Usage
------------


..  code-block:: python

    from lato import DependencyProvider
    import logging
    
    class UserRepository:
        ...
        
    class InMemoryUserRepository(UserRepository):
        ...
    
    logger = logging.getLogger()
    user_repository = InMemoryUserRepository()
    
    dp = DependencyProvider(foo='bar', logger=logger, user_repository=user_repository)

Test
----------------

.. autofunction:: lato.as_type

Creating a dependency provider
----------------

To retrieve a list of random ingredients,
you can use the ``DependencyProvider()`` class:

.. autoclass:: lato.DependencyProvider

The ``kind`` parameter should be either ``"meat"``, ``"fish"``,
or ``"veggies"``. Otherwise, :py:func:`lumache.get_random_ingredients`
will raise an exception.

.. autoexception:: lato.dependency_provider.UnknownDependencyError

For example:

>>> from lato import SimpleDependencyProvider
>>> dp = DependencyProvider(foo='bar')
>>> dp.get_dependency('foo')
'bar'

>>> from lato import SimpleDependencyProvider
>>> dp = DependencyProvider(foo='bar')
>>> dp.get_dependency('foo')
'bar'

>>> from lato import DependencyProvider
>>> dp = DependencyProvider(foo='bar')
>>> dp.get_dependency('foo')
'bar'