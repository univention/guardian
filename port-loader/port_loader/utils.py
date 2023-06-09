import inspect
from functools import wraps, partial
from importlib import metadata
from typing import Type, TYPE_CHECKING, Callable, Any, cast

from loguru import logger

from port_loader.errors import PortInjectionError
from port_loader.models import Adapter, Port

if TYPE_CHECKING:
    from port_loader.registries import AsyncAdapterRegistry


def get_fqcn(cls: Type) -> str:
    """
    Helper function to calculate the fully qualified class name of the given class.
    """

    fqcn = f"{cls.__module__}.{cls.__name__}"
    return fqcn


def is_cached(adapter_to_decorate: Type[Adapter]) -> Type[Adapter]:
    """
    Decorator to use on an adapter class to indicate that this adapter
    should be cached by an adapter registry.

    Internally the class attribute `__port_loader_is_cached` is added
    to the class and set to True.
    """
    setattr(adapter_to_decorate, "__port_loader_is_cached", True)
    logger.bind(adapter=get_fqcn(adapter_to_decorate)).debug(
        "Setting is_cached attribute on adapter class."
    )
    return adapter_to_decorate


def load_from_entry_point(
    adapter_registry: "AsyncAdapterRegistry", port_cls: Type, entry_point_str: str
):
    """
    Helper function to register adapters loaded from entry points.

    The entrypoints for the given string are loaded and registered as adapters for the given
    port with their name as specified by the entry point.

    :param adapter_registry: The registry to register the adapters to
    :param port_cls: The port to register the adapters for
    :param entry_point_str: The name of the entry point group to load
    """
    entry_points = metadata.entry_points().get(entry_point_str, ())
    for entry_point in entry_points:
        adapter_cls = entry_point.load()
        adapter_registry.register_adapter(port_cls, name=entry_point.name)(adapter_cls)


def inject_port(**port_classes: Type[Port]):
    """
    This is a function decorator to inject adapter instances for ports into other functions.

    This works only on classes which have been registered as adapters with an adapter
    registry before.

    Note: As of now this decorator works on async functions only.
    """

    def _inject_port(func: Callable) -> Callable:
        @wraps(func)
        async def _async_wrapper(self, *args, **kwargs) -> Any:
            try:
                registry: AsyncAdapterRegistry = getattr(self, "__port_loader_registry")
            except AttributeError as exc:
                raise PortInjectionError(
                    f"Error during port injection in '{get_fqcn(self.__class__)}'."
                ) from exc
            port_instances = dict()
            for param_name, port_cls in port_classes.items():
                port_instances[param_name] = await registry.get_adapter(port_cls)
            partial_func = partial(func, **port_instances)
            return await partial_func(self, *args, **kwargs)

        if inspect.iscoroutinefunction(func):
            return _async_wrapper
        raise PortInjectionError(
            "Currently the port injection works for async methods only."
        )

    return _inject_port


def injected_port(_port_cls: Type[Port]) -> Port:
    """
    This is a function meant to be used as a default for injected port parameters.
    """
    return cast(Port, object())
