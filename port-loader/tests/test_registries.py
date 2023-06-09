from dataclasses import dataclass
from typing import Type

import pytest
from port_loader import (
    AsyncAdapterSettingsProvider,
    AsyncConfiguredAdapterMixin,
    get_fqcn,
    is_cached,
    Settings,
)
from port_loader.errors import (
    DuplicateAdapterError,
    DuplicatePortError,
    PortTypeError,
    AdapterNotFoundError,
    PortNotFoundError,
    AdapterNotSetError,
    AdapterInstantiationError,
    AdapterConfigurationError,
)


class DummyPort:
    ...


class DummyAdapter(DummyPort):
    ...


@is_cached
class DummyCachedAdapter(DummyPort):
    ...


@dataclass
class DummySettings:
    value: int


class DummySettingsProviderAdapter(AsyncAdapterSettingsProvider):
    async def get_adapter_settings(self, settings_cls: Type[Settings]) -> Settings:
        return settings_cls(value=5)


class DummyAdapterConfigured(DummyPort, AsyncConfiguredAdapterMixin):
    def __init__(self):
        self.settings = None

    @classmethod
    def get_settings_cls(cls) -> Type[Settings]:
        return DummySettings

    async def configure(self, settings: Settings):
        self.settings = settings


class OtherAdapter:
    ...


class TestAsyncAdapterRegistry:
    @staticmethod
    def set_config_port(async_port_loader):
        async_port_loader.register_adapter(
            AsyncAdapterSettingsProvider, set_adapter=True
        )(DummySettingsProviderAdapter)

    def test_settings_provider_port_registered(self, async_port_loader):
        assert (
            async_port_loader._port_configs[
                get_fqcn(AsyncAdapterSettingsProvider)
            ].port_cls
            == AsyncAdapterSettingsProvider
        )

    def test_register_port(self, async_port_loader):
        async_port_loader.register_port(DummyPort)
        assert (
            async_port_loader._port_configs[get_fqcn(DummyPort)].port_cls == DummyPort
        )

    def test_register_port_duplicate_error(self, async_port_loader):
        async_port_loader.register_port(DummyPort)
        with pytest.raises(
            DuplicatePortError,
            match="A port with the name 'test_registries.DummyPort' was already registered.",
        ):
            async_port_loader.register_port(DummyPort)

    def test_register_adapter(self, async_port_loader):
        async_port_loader.register_port(DummyPort)
        async_port_loader.register_adapter(DummyPort)(DummyAdapter)
        assert (
            async_port_loader._adapter_configs[get_fqcn(DummyPort)][
                get_fqcn(DummyAdapter)
            ].adapter_cls
            == DummyAdapter
        )

    def test_register_adapter_port_not_found(self, async_port_loader):
        with pytest.raises(
            PortNotFoundError,
            match="Could not find a port of the class 'test_registries.DummyPort'.",
        ):
            async_port_loader.register_adapter(DummyPort)(DummyAdapter)

    def test_register_adapter_port_type_error(self, async_port_loader):
        async_port_loader.register_port(DummyPort)
        with pytest.raises(
            PortTypeError,
            match="The adapter 'test_registries.OtherAdapter' is not valid for port "
            r"'test_registries.DummyPort'",
        ):
            async_port_loader.register_adapter(DummyPort)(OtherAdapter)

    def test_register_adapter_duplicate_error(self, async_port_loader):
        async_port_loader.register_port(DummyPort)
        async_port_loader.register_adapter(DummyPort)(DummyAdapter)
        with pytest.raises(
            DuplicateAdapterError,
            match="The adapter class 'test_registries.DummyAdapter' has already been "
            "registered for the port 'test_registries.DummyPort'.",
        ):
            async_port_loader.register_adapter(DummyPort)(DummyAdapter)

    def test_register_adapter_cached(self, async_port_loader):
        async_port_loader.register_port(DummyPort)
        async_port_loader.register_adapter(DummyPort)(DummyCachedAdapter)
        assert (
            async_port_loader._adapter_configs[get_fqcn(DummyPort)][
                get_fqcn(DummyCachedAdapter)
            ].is_cached
            is True
        )

    def test_register_adapter_by_name(self, async_port_loader):
        async_port_loader.register_port(DummyPort)
        async_port_loader.register_adapter(DummyPort, name="my_adapter")(DummyAdapter)
        assert (
            async_port_loader._adapter_configs[get_fqcn(DummyPort)][
                get_fqcn(DummyAdapter)
            ].name
            == "my_adapter"
        )

    def test_register_adapter_by_name_duplicate(self, async_port_loader):
        async_port_loader.register_port(DummyPort)
        async_port_loader.register_adapter(DummyPort, name="my_adapter")(DummyAdapter)
        with pytest.raises(
            DuplicateAdapterError,
            match="An adapter class with the name 'my_adapter' has already "
            "been registered for the port test_registries.DummyPort.",
        ):
            async_port_loader.register_adapter(DummyPort, name="my_adapter")(
                DummyCachedAdapter
            )

    def test_register_adapter_configured_settings_adapter(self, async_port_loader):
        class ConfiguredSettings(
            AsyncAdapterSettingsProvider, AsyncConfiguredAdapterMixin
        ):
            async def get_adapter_settings(
                self, settings_cls: Type[Settings]
            ) -> Settings:
                pass

            @classmethod
            def get_settings_cls(cls) -> Type[Settings]:
                pass

            async def configure(self, settings: Settings):
                pass

            ...

        with pytest.raises(
            PortTypeError,
            match="An adapter for the port "
            "'port_loader.adapters.AsyncAdapterSettingsProvider' must never be a ConfiguredAdapter.",
        ):
            async_port_loader.register_adapter(AsyncAdapterSettingsProvider)(
                ConfiguredSettings
            )

    def test_set_adapter(self, async_port_loader):
        async_port_loader.register_port(DummyPort)
        async_port_loader.register_adapter(DummyPort, set_adapter=True)(DummyAdapter)
        assert async_port_loader._port_configs[
            get_fqcn(DummyPort)
        ].selected_adapter == get_fqcn(DummyAdapter)

    def test_set_adapter_by_name(self, async_port_loader):
        async_port_loader.register_port(DummyPort)
        async_port_loader.register_adapter(DummyPort, name="my_adapter")(DummyAdapter)
        async_port_loader.set_adapter(DummyPort, "my_adapter")
        assert async_port_loader._port_configs[
            get_fqcn(DummyPort)
        ].selected_adapter == get_fqcn(DummyAdapter)

    def test_set_adapter_by_name_not_found_error(self, async_port_loader):
        async_port_loader.register_port(DummyPort)
        with pytest.raises(
            AdapterNotFoundError,
            match="No adapter with the name 'my_adapter' was registered "
            "for the port 'test_registries.DummyPort'.",
        ):
            async_port_loader.set_adapter(DummyPort, "my_adapter")

    def test_set_adapter_not_found_error(self, async_port_loader):
        async_port_loader.register_port(DummyPort)
        with pytest.raises(
            AdapterNotFoundError,
            match="No adapter of the type 'test_registries.DummyAdapter' was registered "
            "for the port 'test_registries.DummyPort'",
        ):
            async_port_loader.set_adapter(DummyPort, DummyAdapter)

    @pytest.mark.asyncio
    async def test_get_adapter(self, async_port_loader):
        async_port_loader.register_port(DummyPort)
        async_port_loader.register_adapter(DummyPort, set_adapter=True)(DummyAdapter)
        port = await async_port_loader.get_adapter(DummyPort)
        assert isinstance(port, DummyAdapter)

    @pytest.mark.asyncio
    async def test_get_adapter_by_call(self, async_port_loader):
        async_port_loader.register_port(DummyPort)
        async_port_loader.register_adapter(DummyPort, set_adapter=True)(DummyAdapter)
        port = await async_port_loader(DummyPort)
        assert isinstance(port, DummyAdapter)

    @pytest.mark.asyncio
    async def test_get_adapter_not_set_error(self, async_port_loader):
        async_port_loader.register_port(DummyPort)
        async_port_loader.register_adapter(DummyPort)(DummyAdapter)
        with pytest.raises(
            AdapterNotSetError,
            match="There was no adapter set for the port 'test_registries.DummyPort'.",
        ):
            await async_port_loader.get_adapter(DummyPort)

    @pytest.mark.asyncio
    async def test_get_adapter_instantiation_error(self, async_port_loader):
        class FaultyAdapter(DummyPort):
            def __init__(self):
                raise RuntimeError("I am faulty!")

        async_port_loader.register_port(DummyPort)
        async_port_loader.register_adapter(DummyPort, set_adapter=True)(FaultyAdapter)
        with pytest.raises(
            AdapterInstantiationError,
            match="An error occurred during the instantiation of adapter "
            "'test_registries.FaultyAdapter' for the port test_registries.DummyPort.",
        ):
            await async_port_loader.get_adapter(DummyPort)

    @pytest.mark.parametrize(
        "adapter_cls,should_be_cached",
        [(DummyAdapter, False), (DummyCachedAdapter, True)],
    )
    @pytest.mark.asyncio
    async def test_get_adapter_caching(
        self, async_port_loader, adapter_cls, should_be_cached
    ):
        async_port_loader.register_port(DummyPort)
        async_port_loader.register_adapter(DummyPort, set_adapter=True)(adapter_cls)
        port1 = await async_port_loader.get_adapter(DummyPort)
        port2 = await async_port_loader.get_adapter(DummyPort)
        assert (port1 == port2) == should_be_cached

    @pytest.mark.asyncio
    async def test_get_adapter_configured(self, async_port_loader):
        async_port_loader.register_port(DummyPort)
        async_port_loader.register_adapter(DummyPort, set_adapter=True)(
            DummyAdapterConfigured
        )
        async_port_loader.register_adapter(
            AsyncAdapterSettingsProvider, set_adapter=True
        )(DummySettingsProviderAdapter)
        adapter = await async_port_loader.get_adapter(DummyPort)
        assert adapter.settings.value == 5

    @pytest.mark.asyncio
    async def test_get_adapter_configured_without_provider(self, async_port_loader):
        async_port_loader.register_port(DummyPort)
        async_port_loader.register_adapter(DummyPort, set_adapter=True)(
            DummyAdapterConfigured
        )
        with pytest.raises(AdapterNotSetError):
            await async_port_loader.get_adapter(DummyPort)

    @pytest.mark.asyncio
    async def test_get_adapter_configuration_error(self, async_port_loader):
        class ConfiguredError(DummyPort, AsyncConfiguredAdapterMixin):
            def __init__(self):
                self.settings = None

            @classmethod
            def get_settings_cls(cls) -> Type[Settings]:
                return DummySettings

            def configure(self, settings: Settings):
                raise ValueError

        async_port_loader.register_port(DummyPort)
        async_port_loader.register_adapter(
            AsyncAdapterSettingsProvider, set_adapter=True
        )(DummySettingsProviderAdapter)
        async_port_loader.register_adapter(DummyPort, set_adapter=True)(ConfiguredError)
        with pytest.raises(
            AdapterConfigurationError,
            match="The adapter test_registries.ConfiguredError could not be configured.",
        ):
            await async_port_loader.get_adapter(DummyPort)
