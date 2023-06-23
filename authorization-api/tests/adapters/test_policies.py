# Copyright (C) 2023 Univention GmbH
#
# SPDX-License-Identifier: AGPL-3.0-only

from typing import Callable, Optional

import pytest
from guardian_authorization_api.adapters.policies import OPAAdapter
from guardian_authorization_api.errors import PolicyUpstreamError
from guardian_authorization_api.models.policies import (
    GetPermissionsQuery,
    OPAAdapterSettings,
    Permission,
    PolicyObject,
    Target,
    TargetPermissions,
)


@pytest.fixture
def get_policy_object() -> Callable:
    def _get_policy_object(
        identifier: str,
        roles: Optional[list[str]] = None,
        attributes: Optional[dict] = None,
    ):
        roles = [] if roles is None else roles
        attributes = {} if attributes is None else attributes
        return PolicyObject(id=identifier, roles=roles, attributes=attributes)

    return _get_policy_object


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
            include_general_permissions=include_general_permissions,
        )

    return _get_permissions_query


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
                        "app_name": "app",
                        "namespace_name": "namespace",
                        "name": "permission",
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
                            "app_name": "app",
                            "namespace_name": "namespace",
                            "name": "permission2",
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
