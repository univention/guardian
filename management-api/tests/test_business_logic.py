import pytest
import pytest_asyncio
from fastapi import HTTPException
from guardian_management_api.adapters.app import (
    SQLAppPersistenceAdapter,
)
from guardian_management_api.adapters.context import (
    FastAPIContextAPIAdapter,
    SQLContextPersistenceAdapter,
)
from guardian_management_api.adapters.namespace import (
    SQLNamespacePersistenceAdapter,
)
from guardian_management_api.business_logic import get_contexts
from guardian_management_api.models.routers.base import GetAllRequest
from guardian_management_api.ports.app import AppPersistencePort
from guardian_management_api.ports.context import ContextPersistencePort
from guardian_management_api.ports.namespace import NamespacePersistencePort


@pytest.mark.usefixtures("create_tables")
class TestBusinessLogic:
    @pytest_asyncio.fixture
    async def namespace_sql_adapter(
        self, register_test_adapters
    ) -> SQLNamespacePersistenceAdapter:
        return await register_test_adapters.request_port(NamespacePersistencePort)

    @pytest_asyncio.fixture
    async def app_sql_adapter(self, register_test_adapters) -> SQLAppPersistenceAdapter:
        return await register_test_adapters.request_port(AppPersistencePort)

    @pytest_asyncio.fixture
    async def context_sql_adapter(
        self, register_test_adapters
    ) -> SQLContextPersistenceAdapter:
        return await register_test_adapters.request_port(ContextPersistencePort)

    @pytest.mark.asyncio
    async def test_get_namespaces_internal_error(self, namespace_sql_adapter):
        async def _read_many():
            raise Exception()

        namespace_sql_adapter.read_many = _read_many
        with pytest.raises(HTTPException):
            await get_contexts(
                api_request=GetAllRequest(),
                persistence_port=namespace_sql_adapter,
                api_port=FastAPIContextAPIAdapter(),
            )
