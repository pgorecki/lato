from lato.dependency_provider import SimpleDependencyProvider
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
    dp = SimpleDependencyProvider(a=1, b=2)
    ctx = TransactionContext(dp)
    assert ctx.call(add) == 3


def test_call_with_arg_and_dependency():
    dp = SimpleDependencyProvider(a=10, b=20)
    ctx = TransactionContext(dp)
    assert ctx.call(add, 1) == 21


def test_call_with_kwarg_and_dependency():
    dp = SimpleDependencyProvider(a=10, b=20)
    ctx = TransactionContext(dp)
    assert ctx.call(add, b=2) == 12
