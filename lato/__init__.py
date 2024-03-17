import logging
import typing
from logging import NullHandler

from .application import Application
from .application_module import ApplicationModule
from .compositon import compose
from .dependency_provider import BasicDependencyProvider, DependencyProvider, as_type
from .message import Command, Event, Query
from .transaction_context import TransactionContext

__version__ = "0.10.0"
__all__ = [
    "Application",
    "ApplicationModule",
    "DependencyProvider",
    "BasicDependencyProvider",
    "TransactionContext",
    "Command",
    "Query",
    "Event",
    "as_type",
    "compose",
]


logging.getLogger(__name__).addHandler(NullHandler())


def add_stderr_logger(
    level: int = logging.DEBUG,
) -> logging.StreamHandler:
    """
    Helper for quickly adding a StreamHandler to the logger. Useful for
    debugging.

    Returns the handler after adding it.
    """
    # This method needs to be in this __init__.py to get the __name__ correct
    # even if lato is vendored within another package.
    logger = logging.getLogger(__name__)
    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(message)s"))
    logger.addHandler(handler)
    logger.setLevel(level)
    logger.debug("Added a stderr logging handler to logger: %s", __name__)
    return handler


# ... Clean up.
del NullHandler
