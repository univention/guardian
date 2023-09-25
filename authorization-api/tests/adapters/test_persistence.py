# Copyright (C) 2023 Univention GmbH
#
# SPDX-License-Identifier: AGPL-3.0-only

import json
import os

import pytest
import pytest_asyncio
from guardian_authorization_api.adapters.persistence import (
    StaticDataAdapter,
    UDMPersistenceAdapter,
)
from guardian_authorization_api.errors import ObjectNotFoundError, PersistenceError
from guardian_authorization_api.models.persistence import (
    ObjectType,
    PersistenceObject,
    StaticDataAdapterSettings,
    UDMPersistenceAdapterSettings,
)
from guardian_authorization_api.models.policies import PolicyObject, Role
from guardian_authorization_api.udm_client import (
    UDM,
    NotFound,
    Unauthorized,
    UnprocessableEntity,
)
from guardian_authorization_api.udm_client import (
    ConnectionError as UDMConnectionError,
)

from ..mock_classes import MockUdmObject


def ucs_test_disabled():
    url = os.environ.get("UDM_DATA_ADAPTER__URL")
    username = os.environ.get("UDM_DATA_ADAPTER__USERNAME")
    password = os.environ.get("UDM_DATA_ADAPTER__PASSWORD")
    ucs_test_enabled = os.environ.get("UCS_TEST_ENABLED") == "1"
    if ((url is None) or (username is None) or (password is None)) and ucs_test_enabled:
        raise Exception(
            "UCS integration tests enabled but url, password or username missing"
        )

    return not ucs_test_enabled


@pytest.fixture()
def udm_adapter_settings():
    url = os.environ.get("UDM_DATA_ADAPTER__URL", "http://localhost")
    username = os.environ.get("UDM_DATA_ADAPTER__USERNAME", "Administrator")
    password = os.environ.get("UDM_DATA_ADAPTER__PASSWORD", "univention")
    return UDMPersistenceAdapterSettings(url=url, username=username, password=password)


@pytest_asyncio.fixture
async def udm_adapter(
    udm_adapter_settings: UDMPersistenceAdapterSettings,
) -> UDMPersistenceAdapter:
    adapter = UDMPersistenceAdapter()

    await adapter.configure(udm_adapter_settings)
    return adapter


class TestUDMDataAdapter:
    @pytest.mark.asyncio
    async def test_get_object_unhandled_error(
        self, udm_adapter: UDMPersistenceAdapter, mocker
    ):
        udm_mock = mocker.MagicMock()
        udm_mock.get.side_effect = Exception
        udm_adapter._udm_client = udm_mock
        with pytest.raises(
            PersistenceError,
            match="An unexpected error occurred while fetching data from UDM.",
        ):
            await udm_adapter.get_object("ID", ObjectType.USER)

    @pytest.mark.asyncio
    async def test_get_object_not_supported(self, udm_adapter: UDMPersistenceAdapter):
        with pytest.raises(
            PersistenceError,
            match="The object type 'UNKNOWN' is not supported by UDMPersistenceAdapter.",
        ):
            await udm_adapter.get_object("SOME_OBJECT", ObjectType.UNKNOWN)

    @pytest.mark.asyncio
    @pytest.mark.parametrize("object_type", [ObjectType.USER, ObjectType.GROUP])
    async def test_get_object_not_found(
        self, udm_adapter: UDMPersistenceAdapter, mocker, object_type
    ):
        udm_mock = mocker.MagicMock()
        udm_module_mock = mocker.MagicMock()
        udm_module_mock.get.side_effect = UnprocessableEntity(0, "", None)
        udm_mock.get.return_value = udm_module_mock
        udm_adapter._udm_client = udm_mock
        with pytest.raises(
            ObjectNotFoundError,
            match=f"Could not find object of type '{object_type.name}' with identifier 'NOT_EXISTING'.",
        ):
            await udm_adapter.get_object("NOT_EXISTING", object_type)

    @pytest.mark.asyncio
    async def test_get_object_unauthorized(
        self, udm_adapter: UDMPersistenceAdapter, mocker, udm_adapter_settings
    ):
        udm_mock = mocker.MagicMock()
        udm_mock.get.side_effect = Unauthorized(0, "", None)
        udm_adapter._udm_client = udm_mock
        with pytest.raises(
            PersistenceError,
            match=f"Could not authorize against UDM at '{udm_adapter_settings.url}'.",
        ):
            await udm_adapter.get_object("ID", ObjectType.USER)

    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        "error", [NotFound(0, "", None), UDMConnectionError(0, "", None)]
    )
    async def test_get_object_unreachable(
        self, udm_adapter: UDMPersistenceAdapter, mocker, udm_adapter_settings, error
    ):
        udm_mock = mocker.MagicMock()
        udm_mock.get.side_effect = error
        udm_adapter._udm_client = udm_mock
        with pytest.raises(
            PersistenceError,
            match=f"The UDM at '{udm_adapter_settings.url}' could not be reached.",
        ):
            await udm_adapter.get_object("ID", ObjectType.USER)

    @pytest.mark.asyncio
    @pytest.mark.parametrize("object_type", [ObjectType.USER, ObjectType.GROUP])
    async def test_get_object(
        self, udm_adapter: UDMPersistenceAdapter, mocker, object_type
    ):
        obj_mock = mocker.MagicMock()
        obj_mock.dn = "ID"
        obj_mock.properties = {"a": 1, "b": 2}
        udm_mock = mocker.MagicMock()
        udm_module_mock = mocker.MagicMock()
        udm_module_mock.get.return_value = obj_mock
        udm_mock.get.return_value = udm_module_mock
        udm_adapter._udm_client = udm_mock
        result = await udm_adapter.get_object("ID", object_type)
        udm_module_mock.get.assert_called_once_with("ID")
        assert result == PersistenceObject(
            id="ID", object_type=object_type, attributes={"a": 1, "b": 2}, roles=[]
        )

    @pytest.mark.asyncio
    async def test_lookup_errors(self, udm_adapter: UDMPersistenceAdapter, udm_mock):
        actor_id = "ID"
        users = {
            actor_id: MockUdmObject(
                dn=actor_id,
                properties={
                    "guardianRole": ["ucsschool:users:teacher"],
                    "school": "school1",
                },
            ),
        }

        udm_mock(users=users)

        invalid_id = "abcdefg"
        with pytest.raises(PersistenceError) as excinfo:
            actor_obj, targets = await udm_adapter.lookup_actor_and_old_targets(
                actor_id="ID", old_target_ids=[invalid_id]
            )
        assert f"Cannot determine object type from DN: {invalid_id}" in str(
            excinfo.value
        )

    @pytest.mark.asyncio
    async def test_lookup_targets_users(
        self, udm_adapter: UDMPersistenceAdapter, udm_mock
    ):
        actor_id = "uid=demo_teacher,cn=lehrer,cn=users,ou=DEMOSCHOOL,dc=school,dc=test"
        user_id = (
            "uid=demo_student,cn=schueler,cn=users,ou=DEMOSCHOOL,dc=school,dc=test"
        )
        user_id_2 = (
            "uid=demo_student_2,cn=schueler,cn=users,ou=DEMOSCHOOL,dc=school,dc=test"
        )
        users = {
            user_id: MockUdmObject(
                dn=user_id,
                properties={
                    "guardianRole": ["ucsschool:users:student"],
                    "school": "school1",
                },
            ),
            user_id_2: MockUdmObject(
                dn=user_id_2,
                properties={
                    "guardianRole": ["ucsschool:users:teacher"],
                    "school": "school2",
                },
            ),
            actor_id: MockUdmObject(
                dn=actor_id,
                properties={
                    "guardianRole": ["ucsschool:users:teacher"],
                    "school": "school1",
                },
            ),
        }

        udm_mock(users=users)

        actor_obj, targets = await udm_adapter.lookup_actor_and_old_targets(
            actor_id=actor_id, old_target_ids=[user_id, None, user_id_2, None]
        )
        assert actor_obj == PolicyObject(
            actor_id,
            [Role("ucsschool", "users", "teacher")],
            attributes={"school": "school1"},
        )

        assert targets == [
            PolicyObject(
                id=user_id,
                roles=[Role("ucsschool", "users", "student")],
                attributes={"school": "school1"},
            ),
            None,
            PolicyObject(
                id=user_id_2,
                roles=[Role("ucsschool", "users", "teacher")],
                attributes={"school": "school2"},
            ),
            None,
        ]

    @pytest.mark.asyncio
    async def test_lookup_targets_groups(
        self, udm_adapter: UDMPersistenceAdapter, udm_mock
    ):
        actor_id = "ID"
        group_id = (
            "cn=DEMOSCHOOL-Democlass,cn=klassen,"
            "cn=schueler,cn=groups,ou=DEMOSCHOOL,dc=school,dc=test"
        )
        group_id_2 = (
            "cn=DEMOSCHOOL-Democlass_2,cn=klassen,"
            "cn=schueler,cn=groups,ou=DEMOSCHOOL,dc=school,dc=test"
        )
        users = {
            actor_id: MockUdmObject(
                dn=actor_id,
                properties={
                    "guardianRole": ["ucsschool:users:teacher"],
                    "school": "school1",
                },
            ),
        }

        groups = {
            group_id: MockUdmObject(
                dn=group_id,
                properties={
                    "guardianRole": ["ucsschool:groups:class"],
                    "school": "school1",
                },
            ),
            group_id_2: MockUdmObject(
                dn=group_id_2,
                properties={
                    "guardianRole": ["ucsschool:groups:class"],
                    "school": "school2",
                },
            ),
        }
        udm_mock(users=users, groups=groups)

        actor_obj, targets = await udm_adapter.lookup_actor_and_old_targets(
            actor_id="ID", old_target_ids=[None, group_id, group_id_2]
        )
        assert actor_obj == PolicyObject(
            "ID",
            [Role("ucsschool", "users", "teacher")],
            attributes={"school": "school1"},
        )

        assert targets == [
            None,
            PolicyObject(
                id=group_id,
                roles=[Role("ucsschool", "groups", "class")],
                attributes={"school": "school1"},
            ),
            PolicyObject(
                id=group_id_2,
                roles=[Role("ucsschool", "groups", "class")],
                attributes={"school": "school2"},
            ),
        ]

    def test_udm_client_cached(self, udm_adapter: UDMPersistenceAdapter):
        assert udm_adapter._udm_client is None
        client = udm_adapter.udm_client
        assert isinstance(client, UDM)
        client2 = udm_adapter.udm_client
        assert client is client2
        udm_adapter._udm_client = None
        client3 = udm_adapter.udm_client
        assert client is not client3

    def test_to_policy_role(self):
        assert UDMPersistenceAdapter._to_policy_role("ucsschool:users:teacher") == Role(
            app_name="ucsschool", namespace_name="users", name="teacher"
        )
        with pytest.raises(PersistenceError):
            UDMPersistenceAdapter._to_policy_role("ucsschool-users-teacher")


@pytest.mark.skipif(
    ucs_test_disabled(),
    reason="Cannot run integration tests for UDM adapter if UDM not available",
)
@pytest.mark.integration
class TestUDMDataAdapterIntegration:
    @pytest.mark.asyncio
    async def test_get_user_object(self, udm_adapter: UDMPersistenceAdapter):
        result = await udm_adapter.get_object(
            "uid=Administrator,cn=users,dc=school,dc=test", ObjectType.USER
        )
        assert result.id == "uid=Administrator,cn=users,dc=school,dc=test"
        assert result.object_type == ObjectType.USER
        assert (
            result.attributes["description"]
            == "Built-in account for administering the computer/domain"
        )
        assert result.attributes["displayName"] == "Administrator"

    @pytest.mark.asyncio
    async def test_get_group_object(self, udm_adapter: UDMPersistenceAdapter):
        result = await udm_adapter.get_object(
            "cn=Users,cn=Builtin,dc=school,dc=test", ObjectType.GROUP
        )
        assert result.id == "cn=Users,cn=Builtin,dc=school,dc=test"
        assert result.object_type == ObjectType.GROUP
        assert (
            result.attributes["description"]
            == "Users are prevented from making accidental or intentional "
            "system-wide changes and can run most applications"
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
                "USER1": {"attributes": {"A": 1, "B": 2, "roles": ["role1", "role2"]}},
                "USER2": {"attributes": {}},
                "USER3": {"attributes": 5},
            },
            "groups": {
                "GROUP1": {"attributes": {"C": 3, "D": 4}},
                "GROUP2": {"attributes": {"E": 5, "F": 6, "roles": ["role1", "role2"]}},
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
            roles=mock_data["users"]["USER1"]["attributes"]["roles"],
        )

    @pytest.mark.asyncio
    async def test_get_group(self, loaded_port_instance, mock_data):
        assert await loaded_port_instance.get_object(
            "GROUP2", ObjectType.GROUP
        ) == PersistenceObject(
            object_type=ObjectType.GROUP,
            id="GROUP2",
            attributes=mock_data["groups"]["GROUP2"]["attributes"],
            roles=mock_data["groups"]["GROUP2"]["attributes"]["roles"],
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
