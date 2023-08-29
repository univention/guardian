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
    FastAPINamespaceAPIAdapter,
    SQLNamespacePersistenceAdapter,
)
from guardian_management_api.business_logic import (
    get_contexts,
    get_namespaces,
    get_namespaces_by_app,
)
from guardian_management_api.models.routers.base import GetAllRequest, GetByAppRequest
from guardian_management_api.models.routers.namespace import NamespacesGetRequest
from guardian_management_api.ports.app import AppPersistencePort
from guardian_management_api.ports.context import ContextPersistencePort
from guardian_management_api.ports.namespace import NamespacePersistencePort


@pytest.mark.usefixtures("create_tables")
class TestBusinessLogic:
    @pytest_asyncio.fixture
    async def context_sql_adapter(
        self, register_test_adapters
    ) -> SQLContextPersistenceAdapter:
        return await register_test_adapters.request_port(ContextPersistencePort)

    @pytest_asyncio.fixture
    async def namespace_sql_adapter(
        self, register_test_adapters
    ) -> SQLNamespacePersistenceAdapter:
        return await register_test_adapters.request_port(NamespacePersistencePort)

    @pytest_asyncio.fixture
    async def app_sql_adapter(self, register_test_adapters) -> SQLAppPersistenceAdapter:
        return await register_test_adapters.request_port(AppPersistencePort)

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

    @pytest.mark.asyncio
    async def test_get_namespaces_internal_error(self, namespace_sql_adapter):
        async def _read_many():
            raise Exception()

        namespace_sql_adapter.read_many = _read_many
        with pytest.raises(HTTPException):
            await get_namespaces(
                api_request=NamespacesGetRequest(),
                namespace_persistence_port=namespace_sql_adapter,
                namespace_api_port=FastAPINamespaceAPIAdapter(),
            )

    @pytest.mark.asyncio
    async def test_get_namespaces_by_appname_internal_error(
        self, create_app, sqlalchemy_mixin, namespace_sql_adapter, app_sql_adapter
    ):
        async with sqlalchemy_mixin.session() as session:
            await create_app(session)

        async def _read_many():
            raise Exception()

        namespace_sql_adapter.read_many = _read_many
        with pytest.raises(HTTPException):
            await get_namespaces_by_app(
                api_request=GetByAppRequest(app_name="app"),
                namespace_persistence_port=namespace_sql_adapter,
                namespace_api_port=FastAPINamespaceAPIAdapter(),
            )
