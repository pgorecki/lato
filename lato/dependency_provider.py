import inspect
from typing import Any

from utils import OrderedDict


class UnknownDependencyError(KeyError):
    ...


def is_instance_of_custom_class(x):
    """
    Check if x is an instance of a custom (user-defined) class.

    :param x: Object to check
    :return: True if x is an instance of a custom class, otherwise False
    """
    return hasattr(x, "__class__")


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


class DependencyProvider:
    """
    A dependency provider that manages dependencies and helps in automatic
    dependency injection based on type or parameter name.
    """

    def __init__(self, *args, **kwargs):
        """
        Initialize the DependencyProvider.

        :param args: Class instances to be registered by types
        :param kwargs: Dependencies to be registered by types and with explicit names
        """
        self._dependencies = {}
        self.update(*args, **kwargs)

    def update(self, *args, **kwargs):
        """
        Update the dependency provider with new dependencies.

        :param args:  Class instances to be updated by types
        :param kwargs: Dependencies to be registered by types and with explicit names
        """
        for value in args:
            if is_instance_of_custom_class(value):
                self.register_dependency(value.__class__, value)
            else:
                raise ValueError(
                    f"Got {type(value)}, expected a class. Only class instances can be passed as args. Use kwargs instead."
                )

        for name, value in kwargs.items():
            self.register_dependency(name, value)
            if is_instance_of_custom_class(value):
                self.register_dependency(value.__class__, value)

    def register_dependency(self, identifier: str | type, dependency: Any):
        """
        Register a dependency with a given identifier (name or type).

        :param identifier: The name or type to be used as an identifier for the dependency
        :param dependency: The actual dependency
        """
        if isinstance(identifier, type):
            for c in inspect.getmro(identifier):
                self._dependencies[c] = dependency

        self._dependencies[identifier] = dependency

    def has_dependency(self, identifier: str | type) -> bool:
        """
        Check if a dependency with the given identifier exists.

        :param identifier: Identifier for the dependency
        :return: True if the dependency exists, otherwise False
        """
        return identifier in self._dependencies

    def get_dependency(self, identifier: str | type) -> Any:
        """
        Retrieve a dependency using its identifier (name or type).

        :param identifier: Identifier for the dependency
        :return: The associated dependency
        """
        try:
            return self._dependencies[identifier]
        except KeyError as e:
            raise UnknownDependencyError(identifier)

    def _resolve_arguments(
        self, function_parameters: OrderedDict, overrides: dict[str, Any]
    ) -> dict[str, Any]:
        """
        Resolve given function parameters to their corresponding dependencies.

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
        func: callable,
        func_args: list[Any] = None,
        func_kwargs: dict[str, Any] = None,
    ) -> dict[str, Any]:
        """
        Resolve function parameters by providing necessary kwargs to call the function.

        :param func: The function to get arguments for
        :param func_args: Positional arguments to the function
        :param func_kwargs: Keyword arguments to the function
        :return: A dictionary of keyword arguments
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

    def copy(self, *args, **kwargs) -> "DependencyProvider":
        """
        Create a copy of the dependency provider with updated dependencies.
        :param args: typed overrides
        :param kwargs: named overrides
        :return: A copy of the dependency provider
        """
        dp = DependencyProvider()
        dp._dependencies.update(self._dependencies)
        dp.update(*args, **kwargs)
        return dp
