from typing import Any, Iterable, Tuple, Type, Optional

import pytest
from pydantic import ValidationError

from guardian_authorization_api.adapters import (
    AdapterContainer,
    AdapterSelection,
    load_adapter_classes,
    PORT_CLASSES,
    get_port,
)
from guardian_authorization_api.errors import (
    AdapterInitializationError,
    AdapterLoadingError,
    AdapterConfigurationError,
    SettingNotFoundError,
    SettingTypeError,
)
from guardian_authorization_api.models.ports import ObjectType, PersistenceObject
from guardian_authorization_api.ports import (
    PersistencePort,
    SettingsPort,
    ConfiguredPort,
)


class DummyPersistence(PersistencePort):
    async def get_object(
        self, identifier: str, object_type: ObjectType
    ) -> PersistenceObject:
        pass

    @staticmethod
    def required_settings() -> Iterable[Tuple[str, Type, Any]]:
        return [("A", int, 1), ("B", str, "B")]

    async def configure(self, settings: dict[str, Any]):
        pass

    @property
    def is_singleton(self):
        return True


class DummySettings(SettingsPort):
    async def get_int(self, setting_name: str, default: Optional[int] = None) -> int:
        return default

    async def get_str(self, setting_name: str, default: Optional[str] = None) -> str:
        return default

    async def get_bool(self, setting_name: str, default: Optional[bool] = None) -> bool:
        return default

    @property
    def is_singleton(self):
        return True


@pytest.fixture()
def entry_points_mock(mocker):
    new = mocker.MagicMock()
    settings_ep = mocker.MagicMock()
    settings_ep.name = "dummy"
    settings_ep.load.return_value = DummySettings
    persistence_ep = mocker.MagicMock()
    persistence_ep.name = "dummy"
    persistence_ep.load.return_value = DummyPersistence
    new.return_value = {
        "guardian_authorization_api.SettingsPort": [settings_ep],
        "guardian_authorization_api.PersistencePort": [persistence_ep],
    }
    return new


@pytest.fixture()
def dummy_container():
    selection = AdapterSelection(PersistencePort="dummy", SettingsPort="dummy")
    adapter_classes = {
        "PersistencePort": {"dummy": DummyPersistence},
        "SettingsPort": {"dummy": DummySettings},
    }
    return AdapterContainer(
        adapter_selection=selection, adapter_classes=adapter_classes
    )


class TestAdapterContainer:
    def test_adapter_selection_validation_error(self, dummy_container, mocker):
        dummy_container._adapter_selection = None
        new = mocker.MagicMock(side_effect=ValidationError([], AdapterSelection))
        mocker.patch("guardian_authorization_api.adapters.AdapterSelection", new)
        with pytest.raises(
            AdapterLoadingError,
            match=r"The configuration for the selection of adapters could not be loaded.",
        ):
            _selection = dummy_container.adapter_selection

    def test_adapter_classes_none(self, dummy_container, mocker):
        adapter_classes_dict = {
            "PersistencePort": {"dummy": DummyPersistence},
            "SettingsPort": {"dummy": DummySettings},
        }
        new = mocker.MagicMock(return_value=adapter_classes_dict)
        mocker.patch("guardian_authorization_api.adapters.load_adapter_classes", new)
        dummy_container._adapter_classes = None
        assert dummy_container.adapter_classes == adapter_classes_dict

    def test_instantiate_adapter(self, dummy_container):
        assert isinstance(
            dummy_container._instantiate_adapter(PersistencePort), DummyPersistence
        )

    def test_instantiate_adapter_not_found(self, dummy_container):
        dummy_container._adapter_selection.persistence_port = "other"
        with pytest.raises(
            AdapterInitializationError,
            match=r"The selected adapter 'other' for "
            r"PersistencePort could not be found.",
        ):
            dummy_container._instantiate_adapter(PersistencePort)

    def test_instantiate_adapter_wrong_type(self, dummy_container):
        dummy_container._adapter_classes["PersistencePort"]["dummy"] = DummySettings
        with pytest.raises(
            AdapterInitializationError,
            match=r"The class <class 'test_adapters.DummySettings'> selected as the adapter "
            r"for PersistencePort has the wrong type.",
        ):
            dummy_container._instantiate_adapter(PersistencePort)

    @pytest.mark.asyncio
    async def test_get_adapter_settings(
        self, dummy_container: AdapterContainer, mocker
    ):
        dummy_container.get_adapter = mocker.AsyncMock(
            return_value=DummySettings(mocker.MagicMock())
        )
        settings = await dummy_container._get_adapter_settings(DummyPersistence)
        expected = {"A": 1, "B": "B"}
        assert settings == expected
        assert dummy_container._adapter_settings["DummyPersistence"] == expected

    @pytest.mark.parametrize("error_type", [SettingNotFoundError, SettingTypeError])
    @pytest.mark.asyncio
    async def test_get_adapter_settings_error(
        self, dummy_container: AdapterContainer, mocker, error_type
    ):
        adapter_mock = mocker.AsyncMock()
        adapter_mock.get_setting = mocker.AsyncMock(side_effect=error_type())
        dummy_container.get_adapter = mocker.AsyncMock(return_value=adapter_mock)
        with pytest.raises(AdapterConfigurationError):
            await dummy_container._get_adapter_settings(DummyPersistence)

    @pytest.mark.asyncio
    async def test_configure_adapter(self, dummy_container, mocker):
        settings = {"A": 1, "B": 2}
        conf_mock = mocker.AsyncMock()
        settings_mock = mocker.AsyncMock(return_value=settings)
        dummy_container._get_adapter_settings = settings_mock
        port = DummyPersistence(mocker.MagicMock())
        port.configure = conf_mock
        await dummy_container._configure_adapter(port)
        assert conf_mock.call_args_list == [mocker.call(settings)]

    @pytest.mark.parametrize("error", [ValueError(), AttributeError()])
    @pytest.mark.asyncio
    async def test_configure_adapter_error(self, dummy_container, mocker, error):
        conf_mock = mocker.AsyncMock(side_effect=error)
        settings_mock = mocker.AsyncMock(return_value={})
        dummy_container._get_adapter_settings = settings_mock
        port = DummyPersistence(mocker.MagicMock())
        port.configure = conf_mock
        with pytest.raises(AdapterConfigurationError):
            await dummy_container._configure_adapter(port)

    @pytest.mark.asyncio
    async def test_initialize_adapters(self, dummy_container, mocker):
        get_adapter_mock = mocker.AsyncMock()
        dummy_container.get_adapter = get_adapter_mock
        await dummy_container.initialize_adapters()
        expected = [mocker.call(port_cls) for port_cls in PORT_CLASSES]
        assert get_adapter_mock.call_args_list == expected

    @pytest.mark.asyncio
    async def test_get_adapter_cached(self, dummy_container, mocker):
        port_instance = DummySettings(mocker.MagicMock())
        dummy_container._adapter_instances["DummySettings"] = port_instance
        assert (await dummy_container.get_adapter(DummySettings)) == port_instance

    @pytest.mark.parametrize(
        "is_singleton,adapter_cls",
        [
            (True, DummyPersistence),
            (False, DummyPersistence),
            (True, DummySettings),
            (False, DummySettings),
        ],
    )
    @pytest.mark.asyncio
    async def test_get_adapter_configured(
        self, dummy_container, mocker, is_singleton, adapter_cls
    ):
        port = adapter_cls(mocker.MagicMock())
        adapter_cls.is_singleton = mocker.PropertyMock(return_value=is_singleton)
        conf_mock = mocker.AsyncMock()
        dummy_container._instantiate_adapter = mocker.MagicMock(return_value=port)
        dummy_container._configure_adapter = conf_mock
        returned_port = await dummy_container.get_adapter(PersistencePort)
        assert returned_port == port
        if isinstance(port, ConfiguredPort):
            assert conf_mock.call_args_list == [mocker.call(port)]
        else:
            assert conf_mock.call_args_list == []
        assert ("PersistencePort" in dummy_container._adapter_instances) == is_singleton


def test_load_adapter_classes(entry_points_mock, mocker):
    mocker.patch(
        "guardian_authorization_api.adapters.metadata.entry_points", entry_points_mock
    )
    adapter_classes = load_adapter_classes()
    assert dict(adapter_classes) == {
        "PersistencePort": {"dummy": DummyPersistence},
        "SettingsPort": {"dummy": DummySettings},
    }


def test_load_adapter_classes_duplicate(entry_points_mock, mocker):
    return_value = entry_points_mock.return_value
    return_value["guardian_authorization_api.SettingsPort"] = (
        return_value["guardian_authorization_api.SettingsPort"] * 2
    )
    entry_points_mock.return_value = return_value
    mocker.patch(
        "guardian_authorization_api.adapters.metadata.entry_points", entry_points_mock
    )
    with pytest.raises(
        AdapterLoadingError,
        match=r"There already exists an adapters with the name 'dummy' for the port 'SettingsPort'",
    ):
        load_adapter_classes()


@pytest.mark.asyncio
async def test_get_port(dummy_container, mocker):
    get_adapter_mock = mocker.AsyncMock()
    dummy_container.get_adapter = get_adapter_mock
    wrapper = get_port(SettingsPort, adapter_container=dummy_container)
    await wrapper()
    assert get_adapter_mock.call_args_list == [mocker.call(SettingsPort)]
