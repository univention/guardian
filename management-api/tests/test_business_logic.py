import pytest
import pytest_asyncio
from fastapi import HTTPException
from guardian_management_api.adapters.context import (
    FastAPIContextAPIAdapter,
    SQLContextPersistenceAdapter,
)
from guardian_management_api.business_logic import get_contexts
from guardian_management_api.models.routers.base import GetAllRequest
from guardian_management_api.ports.context import ContextPersistencePort


@pytest.mark.usefixtures("create_tables")
class TestBusinessLogic:
    @pytest_asyncio.fixture
    async def context_sql_adapter(
        self, register_test_adapters
    ) -> SQLContextPersistenceAdapter:
        return await register_test_adapters.request_port(ContextPersistencePort)

    @pytest.mark.asyncio
    async def test_get_contexts_internal_error(self, context_sql_adapter):
        async def _read_many():
            raise Exception()

        context_sql_adapter.read_many = _read_many
        with pytest.raises(HTTPException):
            await get_contexts(
                api_request=GetAllRequest(),
                persistence_port=context_sql_adapter,
                api_port=FastAPIContextAPIAdapter(),
            )
