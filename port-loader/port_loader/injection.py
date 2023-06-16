import inspect
from functools import partial, wraps
from typing import TYPE_CHECKING, Callable, Optional, Type, TypeVar, cast

from port_loader.errors import InjectionError

if TYPE_CHECKING:
    from port_loader import Adapter, AsyncAdapterRegistry, Port  # pragma: no cover

InjectedObject = TypeVar("InjectedObject")


class InjectionDefaultObject:
    """
    This object is a placeholder to be replaced by the actual adapter instance.

    It should never be used or instantiated on its own and only be created by
    the use of the inject_port method.
    """

    def __init__(self, injection_type: Type["Port"]):
        self.injection_type = injection_type


def inject_port(port_cls: "Type[Port]") -> "Port":
    """
    Use this function to mark a parameter as injectable with the specified port.

    This default value will be replaced with the appropriate adapter instance for the port,
    whenever the function is called.

    For this to work, the method has to be decorated with the inject_function decorator.
    This is automatically done for all methods of adapters registered in an adapter registry.

    @inject_function(adapter_registry, {"my_port": MyPortClass})
    def my_method_with_injected_port(param1: int, param2: int = 5, my_port = inject_port(MyPortClass)):
        ...
    """
    return cast("Port", InjectionDefaultObject(port_cls))


def _get_injectable_params(func: Callable) -> dict[str, Type["Port"]]:
    """
    Analyzes a callable and returns all parameters which have InjectionDefaultObject instances
    as default values.

    :raises ValueError: If signature of callable could not be created
    :raises TypeError: If signature of callable could not be created
    """
    signature = inspect.signature(func)
    params = {}
    for param_name, param in signature.parameters.items():
        if isinstance(param.default, InjectionDefaultObject):
            params[param_name] = param.default.injection_type
    return params


def _get_injection_information(
    adapter_cls: "Type[Adapter]",
) -> dict[str, dict[str, "Type[Port]"]]:
    """
    Takes a class and parses through all its methods, static functions and class methods
    to find parameters marked as injectable.

    Returns a dictionary containing the function names as well as the parameters to inject with their
    expected type.
    """
    injectables: dict[str, dict[str, Type["Port"]]] = {}
    members = inspect.getmembers_static(adapter_cls, inspect.isfunction)
    for member_name, member in members:
        try:
            params: dict[str, Type] = _get_injectable_params(member)
            if params:
                injectables[member_name] = _get_injectable_params(member)
        except (ValueError, TypeError):  # pragma: no cover
            continue  # dunder functions and other class members we do not care about.
    return injectables


def inject_function(
    registry: "AsyncAdapterRegistry",
    *,
    params: Optional[dict[str, Type["Port"]]] = None,
    func: Optional[Callable] = None,
):
    """
    This function returns a decorator which injects the decorated function with adapters
    from the given registry.

    If the optional parameter func is supplied, the decorator is immediately applied.
    """

    def _inject_function(func: Callable):
        if not inspect.iscoroutinefunction(func):
            raise InjectionError("Injection currently only works for async functions.")
        parameters: dict[str, Type["Port"]] = (
            params if params else _get_injectable_params(func)
        )

        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            partial_kwargs = {
                param_name: await registry.request_port(adapter_cls)
                for param_name, adapter_cls in parameters.items()
            }
            partial_func = partial(func, **partial_kwargs)
            return await partial_func(*args, **kwargs)

        return async_wrapper

    if func:
        return _inject_function(func)
    return _inject_function


def inject_adapter(
    registry: "AsyncAdapterRegistry", *, adapter_cls: Optional[Type["Adapter"]] = None
):
    """
    This function returns a decorator to inject all methods with ports from the given
    registry.
    If the optional parameter adapter_cls is supplied to this function, the decorator
    is immediately applied.
    """

    def _inject_adapter(adapter_cls: Type["Adapter"]):
        injectables: dict[str, dict[str, Type]] = _get_injection_information(
            adapter_cls
        )
        for injectable_func, params in injectables.items():
            func = getattr(adapter_cls, injectable_func)
            setattr(
                adapter_cls,
                injectable_func,
                inject_function(registry, params=params, func=func),
            )
        return adapter_cls

    if adapter_cls:
        return _inject_adapter(adapter_cls)
    return _inject_adapter
