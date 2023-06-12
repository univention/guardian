import pytest
from port_loader import AsyncAdapterRegistry


@pytest.fixture
def async_port_loader() -> AsyncAdapterRegistry:
    return AsyncAdapterRegistry()
