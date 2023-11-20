# Copyright (C) 2023 Univention GmbH
#
# SPDX-License-Identifier: AGPL-3.0-only

from typing import Optional, Type

import loguru
import pytest
from guardian_lib.ports import BasePort, SettingsPort
from port_loader import Settings
from port_loader.errors import SettingFormatError, SettingTypeError


class TestPort(BasePort):
    ...


def test_logger_property():
    port = TestPort()
    logger1 = port.logger
    logger2 = port.logger
    assert logger1 != logger2
    assert isinstance(logger1, type(loguru.logger))


class BaseAdapter(BasePort):
    ...


class SettingsAdapter(SettingsPort):
    async def get_int(self, setting_name: str, default: Optional[int] = None) -> int:
        pass

    async def get_str(self, setting_name: str, default: Optional[str] = None) -> str:
        pass

    async def get_bool(self, setting_name: str, default: Optional[bool] = None) -> bool:
        pass

    async def get_adapter_settings(self, settings_cls: Type[Settings]) -> Settings:
        pass


class TestBasePort:
    def test_logger(self):
        """
        This test ensures that the logger property always returns a new logger object
        """
        adapter = BaseAdapter()
        assert adapter.logger != adapter.logger


class TestSettingsPort:
    @pytest.mark.parametrize(
        "name,exc_expected",
        [
            ("setting", False),
            ("setting.name4", False),
            ("", True),
            ("my/setting", True),
            ("my.setting.nested.deep.", False),
            ("setting-with-dash", False),
            ("😜", True),
        ],
    )
    def test_check_setting_name_format(self, name, exc_expected):
        if exc_expected:
            with pytest.raises(SettingFormatError):
                SettingsPort.check_setting_name_format(name)
        else:
            SettingsPort.check_setting_name_format(name)

    @pytest.mark.asyncio
    async def test_get_settings(self, mocker):
        get_str_mock = mocker.AsyncMock()
        get_bool_mock = mocker.AsyncMock()
        get_int_mock = mocker.AsyncMock()
        adapter = SettingsAdapter()
        adapter.check_setting_name_format = mocker.MagicMock()
        adapter.get_bool = get_bool_mock
        adapter.get_str = get_str_mock
        adapter.get_int = get_int_mock
        await adapter.get_setting("setting.name", str, "default")
        assert get_str_mock.call_args_list == [mocker.call("setting.name", "default")]
        await adapter.get_setting("setting.name", int, 5)
        assert get_int_mock.call_args_list == [mocker.call("setting.name", 5)]
        await adapter.get_setting("setting.name", bool, True)
        assert get_bool_mock.call_args_list == [mocker.call("setting.name", True)]

    @pytest.mark.asyncio
    async def test_get_settings_type_not_supported(self, mocker):
        adapter = SettingsAdapter()
        adapter.check_setting_name_format = mocker.MagicMock()
        with pytest.raises(
            SettingTypeError,
            match="The requested setting type 'float' is not supported.",
        ):
            await adapter.get_setting("setting.name", float, 0.0)
