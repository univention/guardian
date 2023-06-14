import inspect
from collections import defaultdict
from functools import partial, wraps
from typing import TYPE_CHECKING, Callable, Type, TypeVar, cast

from port_loader.errors import InjectionError

if TYPE_CHECKING:
    from port_loader import Adapter, AsyncAdapterRegistry, Port  # pragma: no cover

InjectedObject = TypeVar("InjectedObject")


class InjectionDefaultObject:
    """
    This object is a placeholder to be replaced by the actual adapter instance.
    """

    def __init__(self, injection_type: "Type[Port]"):
        self.injection_type = injection_type


def inject_port(port_cls: "Type[Port]") -> "Port":
    """
    Use this function to mar a parameter as injectable with the specified port.
    """
    return cast("Port", InjectionDefaultObject(port_cls))


def _get_injection_information(
    adapter_cls: "Type[Adapter]",
) -> dict[str, dict[str, "Type[Adapter]"]]:
    """
    Takes a class and parses through all its methods, static functions and class methods
    to find parameters marked as injectable.

    Returns a dictionary containing the function names as well as the parameters to inject with their
    expected type.
    """
    injectables: dict[str, dict[str, "Type[Adapter]"]] = defaultdict(dict)
    members = inspect.getmembers_static(adapter_cls, inspect.isfunction)
    for member_name, member in members:
        try:
            signature = inspect.signature(member)
        except (ValueError, TypeError):  # pragma: no cover
            continue  # dunder functions and other class members we do not care about.
        for param_name, param in signature.parameters.items():
            if isinstance(param.default, InjectionDefaultObject):
                injectables[member_name][param_name] = param.default.injection_type
    return injectables


def inject_function(registry: "AsyncAdapterRegistry", params: dict[str, "Type[Port]"]):
    """
    Function decorator to inject a function with adapters from the given registry.
    """

    def _inject_function(func: Callable):
        if not inspect.iscoroutinefunction(func):
            raise InjectionError("Injection currently only works for async functions.")

        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            partial_kwargs = {
                param_name: await registry.get_adapter(adapter_cls)
                for param_name, adapter_cls in params.items()
            }
            partial_func = partial(func, **partial_kwargs)
            return await partial_func(*args, **kwargs)

        return async_wrapper

    return _inject_function


def inject_adapter(registry: "AsyncAdapterRegistry"):
    """
    Class decorator to inject all methods with ports from the given registry.
    """

    def _inject_adapter(adapter_cls: "Type[Adapter]"):
        injectables = _get_injection_information(adapter_cls)
        for injectable_func, params in injectables.items():
            func = getattr(adapter_cls, injectable_func)
            setattr(
                adapter_cls, injectable_func, inject_function(registry, params)(func)
            )

    return _inject_adapter
