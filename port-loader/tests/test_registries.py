import inspect
from dataclasses import dataclass
from typing import Type

import pytest
from port_loader import (
    Adapter,
    AsyncAdapterSettingsProvider,
    AsyncConfiguredAdapterMixin,
    Settings,
    get_fqcn,
)
from port_loader.errors import (
    AdapterConfigurationError,
    AdapterInstantiationError,
    AdapterNotFoundError,
    AdapterNotSetError,
    DuplicateAdapterError,
    DuplicatePortError,
    PortNotFoundError,
    PortSubclassError,
)


class TestAsyncAdapterRegistry:
    @pytest.fixture
    def settings_provider(self):
        class SettingsProvider(AsyncAdapterSettingsProvider):
            async def get_adapter_settings(
                self, settings_cls: Type[Settings]
            ) -> Settings:
                return settings_cls()

        return SettingsProvider()

    @pytest.fixture
    def configured_adapter(self, test_port):
        class ConfiguredAdapter(test_port, AsyncConfiguredAdapterMixin):
            @dataclass
            class Settings:
                a: int = 5

            def __init__(self):
                self.settings = None

            @classmethod
            def get_settings_cls(cls) -> Type[Settings]:
                return ConfiguredAdapter.Settings

            async def configure(self, settings: Settings):
                self.settings = settings

        return ConfiguredAdapter

    @pytest.fixture
    def test_port(self):
        class TestPort:
            ...

        return TestPort

    @pytest.fixture
    def test_adapter(self, test_port):
        class TestAdapter(test_port):
            ...

        return TestAdapter

    def test_settings_provider_registered_during_init(self, async_registry):
        assert (
            async_registry._port_configs[
                "port_loader.adapters.AsyncAdapterSettingsProvider"
            ].port_cls
            == AsyncAdapterSettingsProvider
        )

    @pytest.mark.asyncio
    async def test_registry_is_callable(self, mocker, async_registry):
        request_port_mock = mocker.AsyncMock()
        async_registry.request_port = request_port_mock
        await async_registry(int)
        assert request_port_mock.call_args_list == [mocker.call(int)]

    @pytest.mark.asyncio
    async def test_configure_adapter(
        self, mocker, async_registry, settings_provider, configured_adapter
    ):
        adapter = configured_adapter()
        request_port_mock = mocker.AsyncMock(return_value=settings_provider)
        async_registry.request_port = request_port_mock
        await async_registry._configure_adapter(adapter)
        assert adapter.settings.a == 5

    def test_register_port(self, async_registry):
        async_registry.register_port(int)
        assert async_registry._port_configs["builtins.int"].port_cls == int

    def test_register_port_duplicate_error(self, async_registry):
        async_registry.register_port(int)
        with pytest.raises(
            DuplicatePortError,
            match="A port with the name 'builtins.int' was already registered.",
        ):
            async_registry.register_port(int)

    def test_register_adapter_returns_decorator(self, async_registry):
        """Checks that a decorator is returned, if parameter adapter_cls is not supplied."""
        decorator = async_registry.register_adapter(int)
        assert inspect.isfunction(decorator)
        signature = inspect.signature(decorator)
        assert len(signature.parameters) == 1
        assert signature.parameters["adapter_cls"].name == "adapter_cls"
        assert signature.parameters["adapter_cls"].annotation == Type[Adapter]

    def test_register_adapter_configured_settings_provider_error(self, async_registry):
        class ConfiguredSettings(
            AsyncAdapterSettingsProvider, AsyncConfiguredAdapterMixin
        ):
            ...

        with pytest.raises(
            PortSubclassError,
            match="An adapter for the port "
            "'port_loader.adapters.AsyncAdapterSettingsProvider' must never be a ConfiguredAdapter.",
        ):
            async_registry.register_adapter(
                AsyncAdapterSettingsProvider, adapter_cls=ConfiguredSettings
            )

    def test_register_adapter_wrong_type_error(self, async_registry, test_port):
        async_registry.register_port(test_port)
        with pytest.raises(
            PortSubclassError,
            match="The adapter 'builtins.int' is not valid for port 'test_registries.TestPort'",
        ):
            async_registry.register_adapter(test_port, adapter_cls=int)

    def test_register_adapter_port_not_found_error(
        self, async_registry, test_port, test_adapter
    ):
        with pytest.raises(
            PortNotFoundError,
            match="The port 'test_registries.TestPort' was not registered.",
        ):
            async_registry.register_adapter(test_port, adapter_cls=test_adapter)

    def test_register_adapter_duplicate_error(
        self, async_registry, test_port, test_adapter
    ):
        async_registry.register_port(test_port)
        async_registry.register_adapter(test_port, adapter_cls=test_adapter)
        with pytest.raises(
            DuplicateAdapterError,
            match="The adapter class 'test_registries.TestAdapter' has already been "
            "registered for the port 'test_registries.TestPort'.",
        ):
            async_registry.register_adapter(test_port, adapter_cls=test_adapter)

    def test_register_adapter_duplicate_error_by_alias(
        self, async_registry, test_port, test_adapter
    ):
        class Config:
            alias = "test_alias"

        test_adapter.Config = Config
        async_registry.register_port(test_port)
        async_registry.register_adapter(test_port, adapter_cls=test_adapter)
        with pytest.raises(
            DuplicateAdapterError,
            match="An adapter class with the alias 'test_alias' has "
            "already been registered for the port test_registries.TestPort.",
        ):
            async_registry.register_adapter(test_port, adapter_cls=test_adapter)

    @pytest.mark.parametrize(
        "is_cached,alias", [(True, "my_alias"), (False, "my_alias"), (True, None)]
    )
    def test_register_adapter(
        self, mocker, async_registry, test_port, test_adapter, is_cached, alias
    ):
        inject_adapter_mock = mocker.MagicMock()
        mocker.patch("port_loader.registries.inject_adapter", inject_adapter_mock)

        class Config:
            ...

        test_adapter.Config = Config
        test_adapter.Config.alias = alias
        test_adapter.Config.is_cached = is_cached
        async_registry.register_port(test_port)
        async_registry.register_adapter(test_port, adapter_cls=test_adapter)
        adapter_config = async_registry._adapter_configs[get_fqcn(test_port)][
            get_fqcn(test_adapter)
        ]
        assert adapter_config.adapter_cls == test_adapter
        assert adapter_config.alias == alias
        assert adapter_config.is_cached == is_cached
        assert inject_adapter_mock.called_once_with(
            async_registry, adapter_cls=test_adapter
        )

    def test_set_adapter_port_not_found_error(
        self, async_registry, test_port, test_adapter
    ):
        with pytest.raises(
            PortNotFoundError,
            match="The port 'test_registries.TestPort' was not registered.",
        ):
            async_registry.set_adapter(test_port, test_adapter)

    def test_set_adapter_alias_not_found_error(self, async_registry, test_port):
        async_registry.register_port(test_port)
        with pytest.raises(
            AdapterNotFoundError,
            match="No adapter with the alias 'test_adapter' was registered for the "
            "port 'test_registries.TestPort'.",
        ):
            async_registry.set_adapter(test_port, "test_adapter")

    def test_set_adapter_type_not_found_error(
        self, async_registry, test_port, test_adapter
    ):
        async_registry.register_port(test_port)
        with pytest.raises(
            AdapterNotFoundError,
            match="No adapter of the type 'test_registries.TestAdapter' was "
            "registered for the port 'test_registries.TestPort'.",
        ):
            async_registry.set_adapter(test_port, test_adapter)

    @pytest.mark.parametrize("by_alias", [True, False])
    def test_set_adapter(self, async_registry, test_port, test_adapter, by_alias):
        class Config:
            alias = "my_alias"

        test_adapter.Config = Config
        async_registry.register_port(test_port)
        async_registry.register_adapter(test_port, adapter_cls=test_adapter)
        param = "my_alias" if by_alias else test_adapter
        async_registry.set_adapter(test_port, param)
        assert async_registry._port_configs[
            get_fqcn(test_port)
        ].selected_adapter == get_fqcn(test_adapter)

    def test_set_adapter_override(
        self, async_registry, test_port, test_adapter, configured_adapter
    ):
        async_registry.register_port(test_port)
        async_registry.register_adapter(test_port, adapter_cls=test_adapter)
        async_registry.register_adapter(test_port, adapter_cls=configured_adapter)
        async_registry.set_adapter(test_port, test_adapter)
        assert async_registry._port_configs[
            get_fqcn(test_port)
        ].selected_adapter == get_fqcn(test_adapter)
        async_registry.set_adapter(test_port, configured_adapter)
        assert async_registry._port_configs[
            get_fqcn(test_port)
        ].selected_adapter == get_fqcn(configured_adapter)

    @pytest.mark.asyncio
    async def test_request_port_port_not_found_error(self, async_registry, test_port):
        with pytest.raises(
            PortNotFoundError,
            match="The port 'test_registries.TestPort' was not registered.",
        ):
            await async_registry.request_port(test_port)

    @pytest.mark.asyncio
    async def test_request_port_instantiation_error(
        self, async_registry, test_port, test_adapter, register_and_set_adapter
    ):
        def faulty_init(self):
            raise RuntimeError()

        test_adapter.__init__ = faulty_init
        async_registry.register_port(test_port)
        register_and_set_adapter(async_registry, test_port, test_adapter)
        with pytest.raises(
            AdapterInstantiationError,
            match="An error occurred during the instantiation of adapter "
            "'test_registries.TestAdapter' for the port test_registries.TestPort.",
        ):
            await async_registry.request_port(test_port)

    @pytest.mark.asyncio
    async def test_request_port_configuration_error(
        self, async_registry, test_port, configured_adapter, register_and_set_adapter
    ):
        async def faulty_configure(self, settings):
            raise RuntimeError()

        async_registry._configure_adapter = faulty_configure
        async_registry.register_port(test_port)
        register_and_set_adapter(async_registry, test_port, configured_adapter)
        with pytest.raises(
            AdapterConfigurationError,
            match="The adapter test_registries.ConfiguredAdapter could not be configured.",
        ):
            await async_registry.request_port(test_port)

    @pytest.mark.asyncio
    async def test_request_port_no_settings_provider_error(
        self, async_registry, test_port, configured_adapter, register_and_set_adapter
    ):
        """
        This tests the case that we request a configured adapter,
        but no settings provider is present.
        """
        async_registry.register_port(test_port)
        register_and_set_adapter(async_registry, test_port, configured_adapter)
        with pytest.raises(
            AdapterNotSetError,
            match="There was no adapter set for the port "
            "'port_loader.adapters.AsyncAdapterSettingsProvider'.",
        ):
            await async_registry.request_port(test_port)

    @pytest.mark.asyncio
    async def test_request_port(
        self, async_registry, test_port, test_adapter, register_and_set_adapter
    ):
        async_registry.register_port(test_port)
        register_and_set_adapter(async_registry, test_port, test_adapter)
        assert isinstance(await async_registry.request_port(test_port), test_adapter)

    @pytest.mark.asyncio
    async def test_request_port_cached(
        self, async_registry, test_port, test_adapter, register_and_set_adapter
    ):
        class Config:
            is_cached = True

        test_adapter.Config = Config
        async_registry.register_port(test_port)
        register_and_set_adapter(async_registry, test_port, test_adapter)
        instance1 = await async_registry.request_port(test_port)
        instance2 = await async_registry.request_port(test_port)
        assert instance1 == instance2

    @pytest.mark.asyncio
    async def test_request_port_no_adapter_set_no_registered(
        self, async_registry, test_port
    ):
        async_registry.register_port(test_port)
        with pytest.raises(
            AdapterNotSetError,
            match="There was no adapter set for the port 'test_registries.TestPort'.",
        ):
            await async_registry.request_port(test_port)

    @pytest.mark.asyncio
    async def test_request_port_no_adapter_set_one_registered(
        self, async_registry, test_port, test_adapter
    ):
        """
        This test checks that the only adapter registered is returned if no adapter was set,
        but only one was ever registered.
        """
        async_registry.register_port(test_port)
        async_registry.register_adapter(test_port, adapter_cls=test_adapter)
        assert isinstance(await async_registry.request_port(test_port), test_adapter)

    @pytest.mark.asyncio
    async def test_request_port_no_adapter_set_multiple_registered(
        self, async_registry, test_port, test_adapter, configured_adapter
    ):
        async_registry.register_port(test_port)
        async_registry.register_adapter(test_adapter)
        async_registry.register_adapter(configured_adapter)
        with pytest.raises(
            AdapterNotSetError,
            match="There was no adapter set for the port 'test_registries.TestPort'.",
        ):
            await async_registry.request_port(test_port)
