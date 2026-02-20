class DuplicateHandlerError(TypeError):
    """Raised when a Command or Query handler is registered more than once in the same module."""

    ...


class HandlerNotFoundError(LookupError):
    """Raised when no handler is found for a given alias or message."""

    ...


class UnknownDependencyError(KeyError):
    """Raised when a dependency cannot be resolved by the dependency provider."""

    ...
