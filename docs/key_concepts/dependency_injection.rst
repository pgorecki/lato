.. _dependency_injection:


Dependency Injection
====================

work in progress

        Example:
        --------
        >>> from lato.dependency_provider import BasicDependencyProvider
        >>> 
        >>> def my_func(a: str) -> str:
        >>>     print(f"{a} {b}")
        >>>
        >>> assert BasicDependencyProvider(a="foo").resolve_func_params(my_func) == {}

