# Copyright (C) 2023 Univention GmbH
#
# SPDX-License-Identifier: AGPL-3.0-only

import json

import pytest
from guardian_authorization_api.adapters.persistence import StaticDataAdapter
from guardian_authorization_api.errors import ObjectNotFoundError, PersistenceError
from guardian_authorization_api.models.persistence import (
    ObjectType,
    PersistenceObject,
    StaticDataAdapterSettings,
)


class TestStaticDataAdapter:
    """
    For the methods configure and load_static_data we only test the positive cases here,
    since this is a dev-adapter and not suited for production. Exceptions are caught by
    the AdapterContainer.

    If we ever evolve this Adapter to production quality this has to change of course.
    """

    @pytest.fixture
    def mock_data(self):
        return {
            "users": {
                "USER1": {"attributes": {"A": 1, "B": 2}},
                "USER2": {"attributes": {}},
                "USER3": {"attributes": 5},
            },
            "groups": {
                "GROUP1": {"attributes": {"C": 3, "D": 4}},
                "GROUP2": {"attributes": {"E": 5, "F": 6}},
            },
        }

    @pytest.fixture
    def port_instance(self) -> StaticDataAdapter:
        return StaticDataAdapter()

    @pytest.fixture
    def loaded_port_instance(self, port_instance, mock_data):
        port_instance._users = mock_data["users"]
        port_instance._groups = mock_data["groups"]
        return port_instance

    def test_is_cached(self, port_instance):
        assert port_instance.Config.is_cached is True

    @pytest.mark.asyncio
    async def test_get_user(self, loaded_port_instance, mock_data):
        assert await loaded_port_instance.get_object(
            "USER1", ObjectType.USER
        ) == PersistenceObject(
            object_type=ObjectType.USER,
            id="USER1",
            attributes=mock_data["users"]["USER1"]["attributes"],
        )

    @pytest.mark.asyncio
    async def test_get_group(self, loaded_port_instance, mock_data):
        assert await loaded_port_instance.get_object(
            "GROUP2", ObjectType.GROUP
        ) == PersistenceObject(
            object_type=ObjectType.GROUP,
            id="GROUP2",
            attributes=mock_data["groups"]["GROUP2"]["attributes"],
        )

    @pytest.mark.asyncio
    async def test_get_unknown(self, loaded_port_instance):
        with pytest.raises(
            PersistenceError,
            match=r"The object type UNKNOWN is not supported by StaticDataAdapter.",
        ):
            await loaded_port_instance.get_object("USER1", ObjectType.UNKNOWN)

    @pytest.mark.asyncio
    async def test_get_object_not_found(self, loaded_port_instance):
        with pytest.raises(ObjectNotFoundError):
            await loaded_port_instance.get_object("USER99", ObjectType.USER)

    @pytest.mark.asyncio
    async def test_get_object_malformed_attributes(self, loaded_port_instance):
        with pytest.raises(
            PersistenceError,
            match=r"The data of the object with type 'USER' and identifier 'USER3' "
            r"is malformed and could not be loaded.",
        ):
            await loaded_port_instance.get_object("USER3", ObjectType.USER)

    def test_load_static_data(self, port_instance, mock_data, tmp_path):
        directory = tmp_path / "static_data_test"
        directory.mkdir()
        file = directory / "test_data.json"
        file.write_text(json.dumps(mock_data))
        port_instance._load_static_data(str(file))
        assert port_instance._users == mock_data["users"]
        assert port_instance._groups == mock_data["groups"]

    def test_load_static_data_malformed_data(self, port_instance, mock_data, tmp_path):
        directory = tmp_path / "static_data_test"
        directory.mkdir()
        file = directory / "test_data.json"
        file.write_text('{"users": 5, "groups": 4}')
        with pytest.raises(
            RuntimeError, match="The json file did not contain the correct data."
        ):
            port_instance._load_static_data(str(file))

    def test_get_settings_cls(self, port_instance):
        assert port_instance.get_settings_cls() == StaticDataAdapterSettings

    @pytest.mark.asyncio
    async def test_configure(self, port_instance, mocker):
        func_mock = mocker.MagicMock()
        port_instance._load_static_data = func_mock
        await port_instance.configure(
            StaticDataAdapterSettings(data_file_path="some_file")
        )
        assert func_mock.call_args_list == [mocker.call("some_file")]
