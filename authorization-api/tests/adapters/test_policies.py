# Copyright (C) 2023 Univention GmbH
#
# SPDX-License-Identifier: AGPL-3.0-only

import os
from typing import Callable

import pytest
import pytest_asyncio
from guardian_authorization_api.adapters.policies import OPAAdapter
from guardian_authorization_api.errors import PolicyUpstreamError
from guardian_authorization_api.models.policies import (
    CheckPermissionsQuery,
    CheckPermissionsResult,
    CheckResult,
    GetPermissionsQuery,
    Namespace,
    OPAAdapterSettings,
    Permission,
    PolicyObject,
    Target,
    TargetPermissions,
)
from guardian_authorization_api.models.policies import (
    Role as PolicyRole,
)


@pytest.fixture
def get_actor_object(get_policy_object) -> Callable:
    def _get_actor_object():
        return get_policy_object("actor")

    return _get_actor_object


@pytest.fixture
def get_target_object(get_policy_object) -> Callable[[], Target]:
    def _get_target_object():
        return Target(
            old_target=get_policy_object("target"),
            new_target=get_policy_object("target"),
        )

    return _get_target_object


@pytest.fixture
def get_permissions_query(get_actor_object, get_target_object) -> Callable:
    def _get_permissions_query(include_general_permissions: bool = False):
        return GetPermissionsQuery(
            actor=get_actor_object(),
            targets=[get_target_object()],
            namespaces=[Namespace(app_name="app", name="namespace")],
            include_general_permissions=include_general_permissions,
        )

    return _get_permissions_query


@pytest.fixture
def check_permissions_query(get_actor_object, get_target_object) -> Callable:
    def _check_permissions_query(include_general_permissions: bool = False):
        return CheckPermissionsQuery(
            actor=get_actor_object(),
            targets=[get_target_object()],
            namespaces=[Namespace(app_name="app", name="namespace")],
            target_permissions=[
                Permission(
                    app_name="app", namespace_name="namespace", name="permission"
                )
            ],
            general_permissions=[
                Permission(
                    app_name="app", namespace_name="namespace", name="permission2"
                )
            ],
        )

    return _check_permissions_query


class TestOPAAdapter:
    @pytest.fixture
    def port_instance(self):
        return OPAAdapter()

    def test_get_settings_cls(self, port_instance):
        assert port_instance.get_settings_cls() == OPAAdapterSettings

    @pytest.mark.asyncio
    async def test_configure(self, port_instance):
        await port_instance.configure(OPAAdapterSettings(opa_url="URL"))
        assert port_instance._opa_url == "URL"

    @pytest.mark.parametrize("include_general", [True, False])
    @pytest.mark.asyncio
    async def test_get_permissions(
        self,
        mocker,
        port_instance,
        get_permissions_query,
        get_actor_object,
        include_general,
    ):
        check_policy_return_value = [
            {
                "target_id": "target",
                "permissions": [
                    {
                        "appName": "app",
                        "namespace": "namespace",
                        "permission": "permission",
                    }
                ],
            },
        ]
        if include_general:
            check_policy_return_value.append(
                {
                    "target_id": "",
                    "permissions": [
                        {
                            "appName": "app",
                            "namespace": "namespace",
                            "permission": "permission2",
                        }
                    ],
                }
            )
        query = get_permissions_query(include_general)
        opa_client_mock = mocker.AsyncMock()
        opa_client_mock.check_policy.return_value = check_policy_return_value
        port_instance._opa_client = opa_client_mock
        result = await port_instance.get_permissions(query)
        assert result.actor == get_actor_object()
        assert len(result.target_permissions) == 1
        assert result.target_permissions[0] == TargetPermissions(
            target_id="target",
            permissions=[
                Permission(
                    app_name="app", namespace_name="namespace", name="permission"
                )
            ],
        )
        if include_general:
            assert result.general_permissions == [
                Permission(
                    app_name="app", namespace_name="namespace", name="permission2"
                )
            ]
        else:
            assert result.general_permissions is None

    @pytest.mark.asyncio
    async def test_get_permission_upstream_error(
        self, port_instance, get_permissions_query, mocker
    ):
        opa_client_mock = mocker.MagicMock()
        opa_client_mock.check_policy = mocker.AsyncMock(side_effect=RuntimeError)
        port_instance._opa_client = opa_client_mock
        with pytest.raises(
            PolicyUpstreamError, match="Upstream error while getting permissions."
        ):
            await port_instance.get_permissions(get_permissions_query())

    @pytest.mark.asyncio
    async def test_get_permission_faulty_data(
        self, port_instance, get_permissions_query, mocker
    ):
        opa_client_mock = mocker.MagicMock()
        opa_client_mock.check_policy = mocker.AsyncMock(return_value=[{}])
        port_instance._opa_client = opa_client_mock
        with pytest.raises(
            PolicyUpstreamError,
            match="Upstream returned faulty data for get_permissions.",
        ):
            await port_instance.get_permissions(get_permissions_query())

    @pytest.mark.asyncio
    async def test_check_permissions(
        self,
        mocker,
        port_instance,
        check_permissions_query,
        get_actor_object,
    ):
        check_policy_return_value = [
            {
                "target_id": "target",
                "result": True,
            },
            # mock also the response for the empty target
            {
                "target_id": "",
                "result": True,
            },
        ]
        query = check_permissions_query()
        opa_client_mock = mocker.AsyncMock()
        opa_client_mock.check_policy.return_value = check_policy_return_value
        port_instance._opa_client = opa_client_mock
        result = await port_instance.check_permissions(query)
        assert result == CheckPermissionsResult(
            target_permissions=[
                CheckResult(target_id="target", actor_has_permissions=True)
            ],
            actor_has_general_permissions=True,
        )

    @pytest.mark.asyncio
    async def test_check_permission_upstream_error(
        self, port_instance, check_permissions_query, mocker
    ):
        opa_client_mock = mocker.MagicMock()
        opa_client_mock.check_policy = mocker.AsyncMock(side_effect=RuntimeError)
        port_instance._opa_client = opa_client_mock
        with pytest.raises(
            PolicyUpstreamError,
            match="Upstream error while checking targeted permissions.",
        ):
            await port_instance.check_permissions(check_permissions_query())

    @pytest.mark.asyncio
    async def test_check_permission_faulty_data(
        self, port_instance, check_permissions_query, mocker
    ):
        opa_client_mock = mocker.MagicMock()
        opa_client_mock.check_policy = mocker.AsyncMock(return_value=[{}])
        port_instance._opa_client = opa_client_mock
        with pytest.raises(
            PolicyUpstreamError,
            match="Upstream returned faulty data for check_permissions.",
        ):
            await port_instance.check_permissions(check_permissions_query())


def opa_adapter_integrated():
    return os.environ.get("OPA_ADAPTER__URL") is None


@pytest.fixture()
def opa_adapter_settings():
    opa_url: str = os.environ.get("OPA_ADAPTER__URL", "http://localhost:8181")
    return OPAAdapterSettings(opa_url=opa_url)


@pytest_asyncio.fixture
async def opa_adapter(
    opa_adapter_settings: OPAAdapterSettings,
) -> OPAAdapter:
    adapter = OPAAdapter()

    await adapter.configure(opa_adapter_settings)
    return adapter


@pytest.mark.skipif(
    opa_adapter_integrated(),
    reason="Cannot run integration tests for OPA adapter without config",
)
@pytest.mark.in_container
class TestOPAAdapterIntegration:
    @pytest.mark.asyncio
    async def test_get_permissions(
        self,
        opa_adapter: OPAAdapter,
    ):
        query = GetPermissionsQuery(
            actor=PolicyObject(
                id="actor",
                roles=[
                    {
                        "app_name": "ucsschool",
                        "namespace_name": "users",
                        "name": "teacher",
                    }
                ],
                attributes={},
            ),
            targets=[
                Target(
                    old_target=PolicyObject(id="target", roles=[], attributes={}),
                    new_target=PolicyObject(id="target", roles=[], attributes={}),
                )
            ],
            namespaces=[Namespace(app_name="ucsschool", name="users")],
            contexts=None,
            extra_args=None,
            include_general_permissions=True,
        )
        result = await opa_adapter.get_permissions(query=query)
        assert result
        assert result.target_permissions
        assert {
            Permission(app_name="ucsschool", namespace_name="users", name="export"),
            Permission(
                app_name="ucsschool", namespace_name="users", name="read_first_name"
            ),
            Permission(
                app_name="ucsschool", namespace_name="users", name="read_last_name"
            ),
            Permission(
                app_name="ucsschool", namespace_name="users", name="write_password"
            ),
        }.issubset(result.target_permissions[0].permissions)
        assert result.general_permissions
        assert {
            Permission(app_name="ucsschool", namespace_name="users", name="export"),
            Permission(
                app_name="ucsschool", namespace_name="users", name="read_first_name"
            ),
            Permission(
                app_name="ucsschool", namespace_name="users", name="read_last_name"
            ),
            Permission(
                app_name="ucsschool", namespace_name="users", name="write_password"
            ),
        }.issubset(result.general_permissions)

    @pytest.mark.asyncio
    async def test_check_permissions(
        self,
        opa_adapter: OPAAdapter,
    ):
        query = CheckPermissionsQuery(
            actor=PolicyObject(
                id="actor",
                roles=[
                    PolicyRole(
                        app_name="ucsschool", namespace_name="users", name="teacher"
                    )
                ],
                attributes={},
            ),
            targets=[
                Target(
                    old_target=PolicyObject(id="target", roles=[], attributes={}),
                    new_target=PolicyObject(id="target", roles=[], attributes={}),
                ),
            ],
            namespaces=[Namespace(app_name="ucsschool", name="users")],
            target_permissions=[
                Permission(app_name="ucsschool", namespace_name="users", name="export"),
            ],
            general_permissions=[
                Permission(app_name="ucsschool", namespace_name="users", name="export"),
            ],
            contexts=None,
            extra_args=None,
        )
        result = await opa_adapter.check_permissions(query=query)
        assert result
        assert result == CheckPermissionsResult(
            target_permissions=[
                CheckResult(target_id="target", actor_has_permissions=True)
            ],
            actor_has_general_permissions=True,
        )
