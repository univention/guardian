# Copyright (C) 2023 Univention GmbH
#
# SPDX-License-Identifier: AGPL-3.0-only

import pytest
from guardian_authorization_api.business_logic import check_permissions, get_permissions
from guardian_authorization_api.models.policies import CheckPermissionsQuery


@pytest.mark.asyncio
async def test_get_permissions(mocker):
    """
    Since the business logic is just a chain of calls, this test just verifies that
    this chain is followed.
    """
    api_port_mock = mocker.AsyncMock()
    api_port_mock.to_policy_query.return_value = 2
    api_port_mock.to_api_response.return_value = 4
    policy_mock = mocker.AsyncMock()
    policy_mock.get_permissions.return_value = 3
    result = await get_permissions(1, api_port_mock, policy_mock)
    api_port_mock.to_policy_query.assert_called_once_with(1)
    api_port_mock.to_api_response.assert_called_once_with(3)
    policy_mock.get_permissions.assert_called_once_with(2)
    assert result == 4


@pytest.mark.asyncio
async def test_check_permissions(mocker, get_policy_object):
    api_port_mock = mocker.AsyncMock()
    query_return_value = CheckPermissionsQuery(actor=get_policy_object("actor_id"))
    api_port_mock.to_policy_query.return_value = query_return_value
    api_port_mock.to_api_response.return_value = "api_response"
    policy_mock = mocker.AsyncMock()
    policy_mock.check_permissions.return_value = "permissions_result"
    api_port_mock.transform_exception.return_value = Exception()
    result = await check_permissions(
        "permission_check_request", api_port_mock, policy_mock
    )
    api_port_mock.to_policy_query.assert_called_once_with("permission_check_request")
    policy_mock.check_permissions.assert_called_once_with(query_return_value)
    api_port_mock.to_api_response.assert_called_once_with(
        "actor_id", "permissions_result"
    )
    assert result == "api_response"
