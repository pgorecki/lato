import contextlib
from collections.abc import Iterator
from typing import Any

from lato import Application


@contextlib.contextmanager
def override_app(
    application: Application, *args: Any, **kwargs: Any
) -> Iterator[Application]:
    original_dependency_provider = application.dependency_provider
    overridden_dependency_provider = original_dependency_provider.copy(*args, **kwargs)

    application.dependency_provider = overridden_dependency_provider
    yield application

    application.dependency_provider = original_dependency_provider


@contextlib.contextmanager
def override_ctx(
    application: Application, *args: Any, **kwargs: Any
) -> Iterator[Application]:
    original_transaction_context = application.transaction_context

    def overriden_transaction_context(**dependencies: Any) -> Any:
        ctx = original_transaction_context(**dependencies)
        ctx.dependency_provider = ctx.dependency_provider.copy(*args, **kwargs)
        return ctx

    application.transaction_context = overriden_transaction_context  # type: ignore[method-assign]
    yield application

    application.transaction_context = original_transaction_context  # type: ignore[method-assign]


@contextlib.contextmanager
def override(
    application: Application, *args: Any, **kwargs: Any
) -> Iterator[Application]:
    with override_app(application, **kwargs) as overridden1:
        with override_ctx(overridden1, **kwargs) as overridden2:
            yield overridden2
