import pytest

from lato.dependency_provider import BasicDependencyProvider
from lato.message import Command
from lato.transaction_context import TransactionContext


def add(a, b):
    return a + b


def test_call_with_kwargs():
    ctx = TransactionContext()
    assert ctx.call(add, a=1, b=2) == 3


def test_call_with_args():
    ctx = TransactionContext()
    assert ctx.call(add, 1, 2) == 3


def test_call_with_kwargs():
    ctx = TransactionContext()
    assert ctx.call(add, a=1, b=2) == 3


def test_call_with_dependencies():
    dp = BasicDependencyProvider(a=1, b=2)
    ctx = TransactionContext(dp)
    assert ctx.call(add) == 3


def test_call_with_arg_and_dependency():
    dp = BasicDependencyProvider(a=10, b=20)
    ctx = TransactionContext(dp)
    assert ctx.call(add, 1) == 21


def test_call_with_kwarg_and_dependency():
    dp = BasicDependencyProvider(a=10, b=20)
    ctx = TransactionContext(dp)
    assert ctx.call(add, b=2) == 12


def test_call_without_handlers():
    ctx = TransactionContext()
    command = Command()
    with pytest.raises(ValueError):
        ctx.execute(command)
