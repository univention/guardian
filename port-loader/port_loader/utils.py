from importlib import metadata
from typing import TYPE_CHECKING, Type

from loguru import logger

from port_loader.models import Adapter

if TYPE_CHECKING:
    from port_loader.registries import AsyncAdapterRegistry  # pragma: no cover


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
