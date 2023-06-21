import pytest
from guardian_authorization_api.business_logic import get_permissions


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
