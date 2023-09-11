# Copyright (C) 2023 Univention GmbH
#
# SPDX-License-Identifier: AGPL-3.0-only

import pytest
from guardian_authorization_api.business_logic import get_permissions
from guardian_lib.adapter_registry import ADAPTER_REGISTRY
from guardian_lib.adapters.authentication import (
    AlwaysAuthorizedAdapter,
    DuplicatePortError,
)
from guardian_lib.ports import AuthenticationPort


@pytest.mark.asyncio
async def test_get_permissions(mocker):
    """
    Since the business logic is just a chain of calls, this test just verifies that
    this chain is followed.
    """
    try:
        ADAPTER_REGISTRY.register_port(AuthenticationPort)
    except DuplicatePortError:
        pass
    ADAPTER_REGISTRY.register_adapter(
        AuthenticationPort, adapter_cls=AlwaysAuthorizedAdapter
    )
    ADAPTER_REGISTRY.set_adapter(AuthenticationPort, AlwaysAuthorizedAdapter)
    authentication_adapter = await ADAPTER_REGISTRY.request_adapter(
        AuthenticationPort, AlwaysAuthorizedAdapter
    )
    api_port_mock = mocker.AsyncMock()
    api_port_mock.to_policy_query.return_value = 2
    api_port_mock.to_api_response.return_value = 4
    policy_mock = mocker.AsyncMock()
    policy_mock.get_permissions.return_value = 3
    result = await get_permissions(
        1, api_port_mock, policy_mock, authentication_adapter=authentication_adapter
    )
    api_port_mock.to_policy_query.assert_called_once_with(1)
    api_port_mock.to_api_response.assert_called_once_with(3)
    policy_mock.get_permissions.assert_called_once_with(2)
    assert result == 4
