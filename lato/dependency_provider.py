import inspect
from abc import ABC, abstractmethod
from collections.abc import Callable
from typing import Any

from lato.types import DependencyIdentifier
from lato.utils import OrderedDict


class TypedDependency:
    def __init__(self, value, a_type):
        self.value = value
        self.a_type = a_type


def as_type(obj: Any, cls: type) -> TypedDependency:
    return TypedDependency(obj, cls)


class UnknownDependencyError(KeyError):
    ...


def get_function_parameters(func) -> OrderedDict:
    """
    Retrieve the function's parameters and their annotations.

    :param func: The function to inspect
    :return: An ordered dictionary of parameter names to their annotations
    """
    handler_signature = inspect.signature(func)
    kwargs_iterator = iter(handler_signature.parameters.items())
    parameters = OrderedDict()
    for name, param in kwargs_iterator:
        parameters[name] = param.annotation
    return parameters


class DependencyProvider(ABC):
    """A dependency provider interface that provides dependencies and helps in automatic
    dependency injection based on type or parameter name.

    :param allow_names: `True` if dependency resolution by name is supported. Defaults to `True`
    :param allow_types: `True` if dependency resolution by type is supported. Defaults to `True`
    """

    allow_names = True
    allow_types = True

    @abstractmethod
    def has_dependency(self, identifier: DependencyIdentifier) -> bool:
        """
        Check if a dependency with the given identifier exists.

        :param identifier: Identifier for the dependency
        :return: `True` if the dependency exists, `otherwise` False
        """
        raise NotImplementedError()

    @abstractmethod
    def register_dependency(self, identifier: DependencyIdentifier, dependency: Any):
        """
        Register a dependency with a given identifier (name or type).

        :param identifier: The name or type to be used as an identifier for the dependency
        :param dependency: The actual dependency
        """
        raise NotImplementedError()

    def get_dependency(self, identifier: DependencyIdentifier) -> Any:
        """
        Retrieve a dependency using its identifier (name or type).

        :param identifier: Identifier for the dependency
        :return: The associated dependency
        """
        raise NotImplementedError()

    @abstractmethod
    def copy(self, *args, **kwargs) -> "DependencyProvider":
        """Creates a copy of self with updated dependencies.

        :param args: dependencies to update, identified by type.
        :param kwargs: dependencies to update, identified by name and type.
        :return: A copy of the dependency provider.
        """

    def update(self, *args, **kwargs):
        """
        Updates the dependency provider with new dependencies.

        :param args:  dependencies to update, identified by type
        :param kwargs: dependencies to update, identified by name and type
        """
        if self.allow_types:
            for value in args:
                t, v = self._get_type_and_value(value)
                self.register_dependency(t, v)

        for name, value in kwargs.items():
            t, v = self._get_type_and_value(value)
            if self.allow_names:
                self.register_dependency(name, v)
            if self.allow_types:
                self.register_dependency(t, v)

    def _get_type_and_value(self, value):
        if isinstance(value, TypedDependency):
            return value.a_type, value.value
        return type(value), value

    def _resolve_arguments(
        self, function_parameters: OrderedDict, overrides: dict[str, Any]
    ) -> dict[str, Any]:
        """
        Resolves given function parameters to their corresponding dependencies.

        :param function_parameters: Parameters of the function
        :param overrides: Manual overrides for dependencies
        :return: A dictionary of resolved dependencies
        """

        def _resolve(identifier, overrides):
            if identifier in overrides:
                return overrides[identifier]
            return self.get_dependency(identifier)

        kwargs = {}
        for param_name, param_type in function_parameters.items():
            # first, try to resolve by type
            if param_type == inspect.Parameter.empty:
                try:
                    kwargs[param_name] = _resolve(param_type, overrides)
                    continue
                except (ValueError, KeyError):
                    pass
            # then, try to resolve by name
            try:
                kwargs[param_name] = _resolve(param_name, overrides)
                continue
            except (ValueError, KeyError):
                pass

        return kwargs

    def resolve_func_params(
        self,
        func: Callable,
        func_args: Any = None,
        func_kwargs: Any = None,
    ) -> dict[str, Any]:
        """
        Resolves parameters of a function, by matching function parameters to dependencies.

        :param func: The function to get arguments for
        :param func_args: Positional arguments to the function
        :param func_kwargs: Keyword arguments to the function
        :return: A dictionary of resolved dependencies, where the key is the name of the parameter and
            the value is the resolved dependency.
        """

        if func_args is None:
            func_args = []
        if func_kwargs is None:
            func_kwargs = {}

        func_parameters = get_function_parameters(func)
        resolved_kwargs = OrderedDict()
        arg_idx = 0
        for param_name, param_type in func_parameters.items():
            if arg_idx < len(func_args):
                resolved_kwargs[param_name] = func_args[arg_idx]
                arg_idx += 1
                continue

            if param_name in func_kwargs:
                resolved_kwargs[param_name] = func_kwargs[param_name]
            elif param_type != inspect.Parameter.empty and self.has_dependency(
                param_type
            ):
                resolved_kwargs[param_name] = self.get_dependency(param_type)
            elif self.has_dependency(param_name):
                resolved_kwargs[param_name] = self.get_dependency(param_name)

        return resolved_kwargs

    def __getitem__(self, key):
        return self.get_dependency(key)

    def __setitem__(self, key, value):
        self.register_dependency(key, value)


class BasicDependencyProvider(DependencyProvider):
    """
    A dependency provider that manages dependencies and helps in automatic
    dependency injection based on type or parameter name.
    """

    def __init__(self, *args, **kwargs):
        """Initialize the DependencyProvider.

        :param args: Class instances to be registered by types
        :param kwargs: Dependencies to be registered by types and with explicit names
        """
        self._dependencies = {}
        self.update(*args, **kwargs)

    def register_dependency(self, identifier: DependencyIdentifier, dependency: Any):
        """
        Register a dependency with a given identifier (name or type).

        :param identifier: The name or type to be used as an identifier for the dependency
        :param dependency: The actual dependency
        """
        if isinstance(identifier, type):
            self._dependencies[identifier] = dependency

        self._dependencies[identifier] = dependency

    def has_dependency(self, identifier: DependencyIdentifier) -> bool:
        """
        Check if a dependency with the given identifier exists.

        :param identifier: Identifier for the dependency
        :return: True if the dependency exists, otherwise False
        """
        return identifier in self._dependencies

    def get_dependency(self, identifier: DependencyIdentifier) -> Any:
        """
        Retrieve a dependency using its identifier (name or type).

        :param identifier: Identifier for the dependency
        :return: The associated dependency
        """
        try:
            return self._dependencies[identifier]
        except KeyError as e:
            raise UnknownDependencyError(identifier)

    def copy(self, *args, **kwargs) -> DependencyProvider:
        """
        Create a copy of self with updated dependencies.
        :param args: typed overrides
        :param kwargs: named overrides
        :return: A copy of the dependency provider
        """
        dp = BasicDependencyProvider()
        dp._dependencies.update(self._dependencies)
        dp.update(*args, **kwargs)
        return dp
