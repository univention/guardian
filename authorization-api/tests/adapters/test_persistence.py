# Copyright (C) 2023 Univention GmbH
#
# SPDX-License-Identifier: AGPL-3.0-only

import os

import pytest
import pytest_asyncio
from guardian_authorization_api.adapters.persistence import (
    UDMPersistenceAdapter,
)
from guardian_authorization_api.errors import ObjectNotFoundError, PersistenceError
from guardian_authorization_api.models.persistence import (
    ObjectType,
    PersistenceObject,
    UDMPersistenceAdapterSettings,
)
from guardian_authorization_api.models.policies import Context, PolicyObject, Role
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


def udm_test_disabled():
    url = os.environ.get("UDM_DATA_ADAPTER__URL")
    username = os.environ.get("UDM_DATA_ADAPTER__USERNAME") or os.environ.get(
        "UDM_DATA_ADAPTER__USERNAME_FILE"
    )
    password = os.environ.get("UDM_DATA_ADAPTER__PASSWORD") or os.environ.get(
        "UDM_DATA_ADAPTER__PASSWORD_FILE"
    )
    return (url is None) or (username is None) or (password is None)


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
        udm_module_mock.get.assert_called_once_with(
            "ID", properties=["guardianInheritedRoles", "*"]
        )
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
                    "guardianRoles": ["ucsschool:users:teacher"],
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
    @pytest.mark.parametrize(
        "properties",
        [
            {
                "user_0": {
                    "guardianRoles": ["ucsschool:users:student"],
                    "school": "school1",
                },
                "user_1": {
                    "guardianRoles": ["ucsschool:users:teacher"],
                    "school": "school2",
                },
                "actor": {
                    "guardianRoles": ["ucsschool:users:teacher"],
                    "school": "school1",
                },
            },
            {
                "user_0": {
                    "guardianInheritedRoles": ["ucsschool:users:student"],
                    "school": "school1",
                },
                "user_1": {
                    "guardianInheritedRoles": ["ucsschool:users:teacher"],
                    "school": "school2",
                },
                "actor": {
                    "guardianInheritedRoles": ["ucsschool:users:teacher"],
                    "school": "school1",
                },
            },
            {
                "user_0": {
                    "guardianInheritedRoles": ["ucsschool:users:student"],
                    "guardianRoles": ["ucsschool:users:student"],
                    "school": "school1",
                },
                "user_1": {
                    "guardianInheritedRoles": ["ucsschool:users:teacher"],
                    "guardianRoles": ["ucsschool:users:teacher"],
                    "school": "school2",
                },
                "actor": {
                    "guardianInheritedRoles": ["ucsschool:users:teacher"],
                    "guardianRoles": ["ucsschool:users:teacher"],
                    "school": "school1",
                },
            },
        ],
    )
    async def test_lookup_targets_users(
        self, udm_adapter: UDMPersistenceAdapter, udm_mock, properties
    ):
        """Test the lookup of target users and their conversion to PolicyObjects

        All listed `properties` parametrizations must be result in equivalent objects.
        """
        actor_id = "uid=demo_teacher,cn=lehrer,cn=users,ou=DEMOSCHOOL,dc=school,dc=test"
        user_id_0 = (
            "uid=demo_student,cn=schueler,cn=users,ou=DEMOSCHOOL,dc=school,dc=test"
        )
        user_id_1 = (
            "uid=demo_student_2,cn=schueler,cn=users,ou=DEMOSCHOOL,dc=school,dc=test"
        )
        users = {
            user_id_0: MockUdmObject(dn=user_id_0, properties=properties["user_0"]),
            user_id_1: MockUdmObject(dn=user_id_1, properties=properties["user_1"]),
            actor_id: MockUdmObject(dn=actor_id, properties=properties["actor"]),
        }

        udm_mock(users=users)

        actor_obj, targets = await udm_adapter.lookup_actor_and_old_targets(
            actor_id=actor_id, old_target_ids=[user_id_0, None, user_id_1, None]
        )
        assert actor_obj == PolicyObject(
            actor_id,
            [Role("ucsschool", "users", "teacher")],
            attributes={"school": "school1"},
        )

        assert targets == [
            PolicyObject(
                id=user_id_0,
                roles=[Role("ucsschool", "users", "student")],
                attributes={"school": "school1"},
            ),
            None,
            PolicyObject(
                id=user_id_1,
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
                    "guardianRoles": ["ucsschool:users:teacher"],
                    "school": "school1",
                },
            ),
        }

        groups = {
            group_id: MockUdmObject(
                dn=group_id,
                properties={
                    "guardianRoles": ["ucsschool:groups:class"],
                    "school": "school1",
                },
            ),
            group_id_2: MockUdmObject(
                dn=group_id_2,
                properties={
                    "guardianRoles": ["ucsschool:groups:class"],
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

    def test_to_policy_role_with_context(self):
        context = Context(app_name="ucsschool", namespace_name="users", name="school1")
        assert UDMPersistenceAdapter._to_policy_role(
            "ucsschool:users:teacher&ucsschool:users:school1"
        ) == Role(
            app_name="ucsschool",
            namespace_name="users",
            name="teacher",
            context=context,
        )
        with pytest.raises(PersistenceError):
            UDMPersistenceAdapter._to_policy_role("ucsschool:users:teacher&funky-role")


@pytest.mark.skipif(
    udm_test_disabled(),
    reason="Cannot run integration tests for UDM adapter if UDM configuration is not available",
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

    @pytest.mark.asyncio
    async def test_get_user_with_role(
        self,
        create_test_user_with_udm: callable,
        udm_adapter: UDMPersistenceAdapter,
    ):
        guardian_roles = ["guardian:builtin:super-admin"]
        user_obj = create_test_user_with_udm(guardian_roles=guardian_roles)

        actual_persistence_object = await udm_adapter.get_object(
            user_obj.dn, ObjectType.USER
        )

        expected_persistence_object = PersistenceObject(
            id=user_obj.dn,
            object_type=ObjectType.USER,
            attributes=user_obj.properties,
            roles=guardian_roles,
        )
        assert expected_persistence_object == actual_persistence_object

    @pytest.mark.asyncio
    async def test_get_user_with_inherited_role(
        self,
        create_test_user_with_udm: callable,
        create_test_group_with_udm: callable,
        udm_adapter: UDMPersistenceAdapter,
    ):
        guardian_member_roles = ["guardian:builtin:super-admin"]
        group_obj = create_test_group_with_udm(
            guardian_member_roles=guardian_member_roles
        )

        user_obj = create_test_user_with_udm(groups=[group_obj.dn])

        actual_persistence_object = await udm_adapter.get_object(
            user_obj.dn, ObjectType.USER
        )

        expected_persistence_object = PersistenceObject(
            id=user_obj.dn,
            object_type=ObjectType.USER,
            attributes=user_obj.properties,
            roles=guardian_member_roles,
        )

        breakpoint()
        assert expected_persistence_object == actual_persistence_object
