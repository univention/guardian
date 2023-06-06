import os

import pytest

from guardian_authorization_api.errors import (
    SettingFormatError,
    SettingNotFoundError,
    SettingTypeError,
)
from guardian_authorization_api.settings import EnvSettingsAdapter


class TestEnvSettings:
    @pytest.fixture
    def port_instance(self, mocker):
        return EnvSettingsAdapter(mocker.MagicMock())

    @pytest.fixture(scope="session")
    def mock_env(self):
        return {
            "NUMBER_ONE": "1",
            "NUMBER_TWO": "2",
            "NESTED__VALUE": "1",
            "FALSE": "0",
            "TRUE": "1",
            "SOME_STRING": "some string",
        }

    @pytest.fixture(autouse=True)
    def apply_mock_env(self, mocker, mock_env):
        mocker.patch.dict(os.environ, mock_env)

    @pytest.mark.parametrize(
        "name,expected",
        [
            ("setting_name", "SETTING_NAME"),
            ("", ""),
            ("setting.name", "SETTING__NAME"),
            ("setting_.name", "SETTING___NAME"),
        ],
    )
    def test_setting_name_to_env(self, name, expected):
        assert EnvSettingsAdapter.setting_name_to_env(name) == expected

    @pytest.mark.parametrize(
        "setting_name",
        ["this_is_not_ASCII_😀", "contains space", "has_special_character;"],
    )
    @pytest.mark.asyncio
    async def test_get_setting_wrong_format(self, port_instance, setting_name):
        with pytest.raises(SettingFormatError):
            await port_instance.get_setting(setting_name, str)

    @pytest.mark.parametrize(
        "setting_name,setting_type,expected",
        [
            ("NUMBER_ONE", int, 1),
            ("NUMBER_TWO", str, "2"),
            ("NESTED.VALUE", int, 1),
            ("NUMBER_ONE", bool, True),
            ("FALSE", bool, False),
        ],
    )
    @pytest.mark.asyncio
    async def test_get_setting(
        self, port_instance, setting_name, setting_type, expected
    ):
        assert (
            await port_instance.get_setting(setting_name, setting_type, None)
            == expected
        )

    @pytest.mark.parametrize(
        "setting_type,default", [(int, 5), (bool, True), (str, "string")]
    )
    @pytest.mark.asyncio
    async def test_get_settings_default(self, port_instance, setting_type, default):
        assert (
            await port_instance.get_setting("NON_EXISTENT", setting_type, default)
            == default
        )

    @pytest.mark.parametrize("setting_type", [str, bool, int])
    @pytest.mark.asyncio
    async def test_get_setting_not_found(self, port_instance, setting_type):
        with pytest.raises(SettingNotFoundError):
            await port_instance.get_setting("NON_EXISTENT", setting_type)

    @pytest.mark.asyncio
    async def test_get_setting_type_error(self, port_instance):
        with pytest.raises(
            SettingTypeError,
            match=r"The requested setting type 'float' is not supported.",
        ):
            await port_instance.get_setting("NUMBER_ONE", float)

    @pytest.mark.asyncio
    async def test_get_int_type_error(self, port_instance):
        with pytest.raises(
            SettingTypeError,
            match=r"The value 'some string' for the setting SOME_STRING could not "
            r"be transformed to an integer.",
        ):
            await port_instance.get_int("SOME_STRING")

    @pytest.mark.parametrize(
        "setting_name,expected", [("TRUE", True), ("FALSE", False)]
    )
    @pytest.mark.asyncio
    async def test_get_bool(self, port_instance, setting_name, expected):
        assert await port_instance.get_bool(setting_name) == expected

    @pytest.mark.asyncio
    async def test_get_bool_default(self, port_instance):
        assert await port_instance.get_bool("NON_EXISTENT", True) is True

    @pytest.mark.asyncio
    async def test_get_bool_not_found(self, port_instance):
        with pytest.raises(SettingNotFoundError):
            await port_instance.get_bool("NON_EXISTENT")

    @pytest.mark.asyncio
    async def test_get_bool_type_error(self, port_instance):
        with pytest.raises(SettingTypeError):
            await port_instance.get_bool("SOME_STRING")

    @pytest.mark.parametrize(
        "setting_type,default", [(bool, False), (str, ""), (int, 0)]
    )
    @pytest.mark.asyncio
    async def test_falsy_defaults(self, port_instance, setting_type, default):
        assert (
            await port_instance.get_setting("NON_EXISTENT", setting_type, default)
            == default
        )

    def test_is_singleton(self, port_instance):
        assert port_instance.is_singleton is True
