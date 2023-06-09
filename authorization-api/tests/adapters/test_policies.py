from typing import Callable

import pytest

from guardian_authorization_api.adapters.policies import OPAAdapter
from guardian_authorization_api.errors import PolicyUpstreamError
from guardian_authorization_api.models.policies import PolicyObject


class TestOPAAdapter:
    @pytest.fixture
    def port_instance(self):
        return OPAAdapter()

    @pytest.fixture
    def get_actor_object(self) -> Callable[[], PolicyObject]:
        def _get_actor_object():
            return PolicyObject(id="actor", attributes={}, roles=[])

        return _get_actor_object

    @pytest.mark.asyncio
    async def test_get_permission_upstream_error(
        self, port_instance, get_actor_object, mocker
    ):
        opa_client_mock = mocker.MagicMock()
        opa_client_mock.check_policy = mocker.AsyncMock(side_effect=RuntimeError)
        port_instance._opa_client = opa_client_mock
        with pytest.raises(
            PolicyUpstreamError, match="Upstream error while getting permissions."
        ):
            await port_instance.get_permissions(get_actor_object())

    @pytest.mark.asyncio
    async def test_get_permission_faulty_data(
        self, port_instance, get_actor_object, mocker
    ):
        opa_client_mock = mocker.MagicMock()
        opa_client_mock.check_policy = mocker.AsyncMock(return_value=[{}])
        port_instance._opa_client = opa_client_mock
        with pytest.raises(
            PolicyUpstreamError,
            match="Upstream returned faulty data for get_permissions.",
        ):
            await port_instance.get_permissions(get_actor_object())
