from dataclasses import dataclass
from typing import TypeVar, Generic, Type, Optional

Adapter = TypeVar("Adapter")
Port = TypeVar("Port")
Settings = TypeVar("Settings")


@dataclass
class AdapterConfiguration(Generic[Adapter]):
    """
    This dataclass represents a configuration of an adapter registered to
    an adapter registry.
    """

    adapter_cls: Type[Adapter]
    is_cached: bool
    name: Optional[str] = None


@dataclass
class PortConfiguration(Generic[Port]):
    """
    This dataclass represents a configuration of a port registered to
    an adapter registry.
    """

    port_cls: Type[Port]
    selected_adapter: Optional[str] = None
