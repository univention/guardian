import guardian_lib.adapter_registry as adapter_registry
import pytest
from guardian_lib.adapters.authentication import (
    FastAPIAlwaysAuthorizedAdapter,
    FastAPINeverAuthorizedAdapter,
    FastAPIOAuth2,
)
from guardian_lib.adapters.settings import EnvSettingsAdapter
from guardian_lib.ports import AuthenticationPort, SettingsPort
from port_loader import AsyncAdapterRegistry, AsyncAdapterSettingsProvider
from port_loader.errors import DuplicatePortError


@pytest.fixture()
def env_settings(monkeypatch):
    monkeypatch.setenv("OAUTH_ADAPTER__WELL_KNOWN_URL", "http://example.com")
    monkeypatch.setenv("OAUTH_ADAPTER__WELL_KNOWN_URL_SECURE", "True")


@pytest.fixture()
def register_test_adapters(env_settings):
    for port, adapter in [
        (SettingsPort, EnvSettingsAdapter),
        (AsyncAdapterSettingsProvider, EnvSettingsAdapter),
        (AuthenticationPort, FastAPIAlwaysAuthorizedAdapter),
        (AuthenticationPort, FastAPINeverAuthorizedAdapter),
        (AuthenticationPort, FastAPIOAuth2),
    ]:
        try:
            adapter_registry.ADAPTER_REGISTRY.register_port(port)
        except DuplicatePortError:
            pass
        adapter_registry.ADAPTER_REGISTRY.register_adapter(port, adapter_cls=adapter)
        adapter_registry.ADAPTER_REGISTRY.set_adapter(port, adapter)
    yield adapter_registry.ADAPTER_REGISTRY
    adapter_registry.ADAPTER_REGISTRY = AsyncAdapterRegistry()
