import pytest
import pytest_asyncio
from fastapi import HTTPException
from guardian_lib.ports import AuthenticationPort
from guardian_management_api import business_logic
from guardian_management_api.adapters.app import (
    FastAPIAppAPIAdapter,
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
    create_app,
    get_apps,
    get_contexts,
    get_namespaces,
    get_namespaces_by_app,
)
from guardian_management_api.errors import DependencyExistsError, UnauthorizedError
from guardian_management_api.models.authz import ResourceType
from guardian_management_api.models.routers.app import AppCreateRequest, AppsGetRequest
from guardian_management_api.models.routers.base import GetAllRequest, GetByAppRequest
from guardian_management_api.models.routers.namespace import NamespacesGetRequest
from guardian_management_api.ports.app import AppPersistencePort
from guardian_management_api.ports.authz import ResourceAuthorizationPort
from guardian_management_api.ports.context import ContextPersistencePort
from guardian_management_api.ports.namespace import NamespacePersistencePort
from httpx import Request


async def transform_exception_identity(exc: Exception):
    return exc


@pytest.mark.usefixtures("create_tables")
class TestBusinessLogic:
    @pytest_asyncio.fixture
    async def context_sql_adapter(
        self, registry_test_adapters
    ) -> SQLContextPersistenceAdapter:
        return await registry_test_adapters.request_port(ContextPersistencePort)

    @pytest_asyncio.fixture
    async def namespace_sql_adapter(
        self, registry_test_adapters
    ) -> SQLNamespacePersistenceAdapter:
        return await registry_test_adapters.request_port(NamespacePersistencePort)

    @pytest_asyncio.fixture
    async def app_sql_adapter(self, registry_test_adapters) -> SQLAppPersistenceAdapter:
        return await registry_test_adapters.request_port(AppPersistencePort)

    @pytest_asyncio.fixture
    async def app_authc_adapter(self, registry_test_adapters):
        return await registry_test_adapters.request_port(AuthenticationPort)

    @pytest_asyncio.fixture
    async def app_authz_adapter(self, registry_test_adapters):
        return await registry_test_adapters.request_port(ResourceAuthorizationPort)

    @pytest.mark.asyncio
    async def test_get_contexts_internal_error(self, context_sql_adapter, mocker):
        async def _read_many():
            raise Exception()

        context_sql_adapter.read_many = _read_many
        authz_mock = mocker.AsyncMock()
        authz_mock.authorize_operation = mocker.AsyncMock(return_value={"test": False})
        authc_mock = mocker.AsyncMock()
        request = mocker.Mock()
        with pytest.raises(HTTPException):
            await get_contexts(
                api_request=GetAllRequest(),
                persistence_port=context_sql_adapter,
                api_port=FastAPIContextAPIAdapter(),
                authc_port=authc_mock,
                authz_port=authz_mock,
                request=request,
            )

    @pytest.mark.asyncio
    async def test_get_namespaces_internal_error(self, namespace_sql_adapter, mocker):
        async def _read_many():
            raise Exception()

        namespace_sql_adapter.read_many = _read_many
        authz_mock = mocker.AsyncMock()
        authz_mock.authorize_operation = mocker.AsyncMock(return_value={"test": False})
        authc_mock = mocker.AsyncMock()
        request = mocker.Mock()
        with pytest.raises(HTTPException):
            await get_namespaces(
                api_request=NamespacesGetRequest(),
                namespace_persistence_port=namespace_sql_adapter,
                namespace_api_port=FastAPINamespaceAPIAdapter(),
                authc_port=authc_mock,
                authz_port=authz_mock,
                request=request,
            )

    @pytest.mark.asyncio
    async def test_get_namespaces_by_appname_internal_error(
        self,
        create_app,
        sqlalchemy_mixin,
        namespace_sql_adapter,
        app_sql_adapter,
        mocker,
    ):
        async with sqlalchemy_mixin.session() as session:
            await create_app(session)

        async def _read_many():
            raise Exception()

        namespace_sql_adapter.read_many = _read_many
        authz_mock = mocker.AsyncMock()
        authz_mock.authorize_operation = mocker.AsyncMock(return_value={"test": False})
        authc_mock = mocker.AsyncMock()
        request = mocker.Mock()
        with pytest.raises(HTTPException):
            await get_namespaces_by_app(
                api_request=GetByAppRequest(app_name="app"),
                namespace_persistence_port=namespace_sql_adapter,
                namespace_api_port=FastAPINamespaceAPIAdapter(),
                authc_port=authc_mock,
                authz_port=authz_mock,
                request=request,
            )

    @pytest.mark.asyncio
    async def test_create_app_internal_error(
        self, app_sql_adapter, app_authc_adapter, app_authz_adapter
    ):
        async def _create():
            raise Exception()

        app_sql_adapter.create = _create
        with pytest.raises(HTTPException) as exc_info:
            await create_app(
                api_request=AppCreateRequest(name="app"),
                app_api_port=FastAPIAppAPIAdapter(),
                persistence_port=app_sql_adapter,
                authc_port=app_authc_adapter,
                authz_port=app_authz_adapter,
                request=Request("POST", "something"),
            )
        assert exc_info.value.status_code == 500
        assert exc_info.value.detail == {"message": "Internal Server Error"}

    @pytest.mark.asyncio
    async def test_get_apps_internal_error(
        self, app_sql_adapter, app_authc_adapter, app_authz_adapter
    ):
        async def _read_many():
            raise Exception()

        app_sql_adapter.read_many = _read_many
        with pytest.raises(HTTPException) as exc_info:
            await get_apps(
                api_request=AppsGetRequest(),
                app_api_port=FastAPIAppAPIAdapter(),
                persistence_port=app_sql_adapter,
                authc_port=app_authc_adapter,
                authz_port=app_authz_adapter,
                request=Request("GET", "something"),
            )
        assert exc_info.value.status_code == 500
        assert exc_info.value.detail == {"message": "Internal Server Error"}

    @pytest.mark.asyncio
    async def test_create_app_unauthorized_error(self, mocker):
        api_request_mock = mocker.MagicMock()
        api_port_mock = mocker.AsyncMock()
        api_port_mock.transform_exception = transform_exception_identity
        persistence_mock = mocker.AsyncMock()
        authz_mock = mocker.AsyncMock()
        authz_mock.authorize_operation = mocker.AsyncMock(return_value={"test": False})
        authc_mock = mocker.AsyncMock()
        request = mocker.Mock()
        with pytest.raises(
            UnauthorizedError,
            match="The logged in user is not authorized to create this app.",
        ):
            await business_logic.create_app(
                api_request_mock,
                api_port_mock,
                persistence_mock,
                authc_mock,
                authz_mock,
                request,
            )

    @pytest.mark.asyncio
    async def test_get_app_unauthorized_error(self, mocker):
        api_request_mock = mocker.MagicMock()
        api_port_mock = mocker.AsyncMock()
        api_port_mock.transform_exception = transform_exception_identity
        persistence_mock = mocker.AsyncMock()
        authz_mock = mocker.AsyncMock()
        authz_mock.authorize_operation = mocker.AsyncMock(return_value={"test": False})
        authc_mock = mocker.AsyncMock()
        request = mocker.Mock()
        with pytest.raises(
            UnauthorizedError,
            match="The logged in user is not authorized to read this app.",
        ):
            await business_logic.get_app(
                api_request_mock,
                api_port_mock,
                persistence_mock,
                authc_mock,
                authz_mock,
                request,
            )

    @pytest.mark.asyncio
    async def test_get_apps_none_authorized(self, mocker):
        api_request_mock = mocker.MagicMock()
        api_port_mock = mocker.AsyncMock()
        api_port_mock.transform_exception = transform_exception_identity
        persistence_mock = mocker.AsyncMock()
        authz_mock = mocker.AsyncMock()
        authz_mock.authorize_operation = mocker.AsyncMock(return_value={"test": False})
        authc_mock = mocker.AsyncMock()
        request = mocker.Mock()
        await business_logic.get_apps(
            api_request_mock,
            api_port_mock,
            persistence_mock,
            authc_mock,
            authz_mock,
            request,
        )
        assert api_port_mock.to_api_apps_get_response.call_args.kwargs["apps"] == []

    @pytest.mark.asyncio
    async def test_register_app_unauthorized_error(self, mocker):
        generic_mock = mocker.MagicMock()
        api_port_mock = mocker.AsyncMock()
        api_port_mock.transform_exception = transform_exception_identity
        authz_mock = mocker.AsyncMock()
        authz_mock.authorize_operation = mocker.AsyncMock(return_value={"test": False})
        authc_mock = mocker.AsyncMock()
        request = mocker.Mock()
        with pytest.raises(
            UnauthorizedError,
            match="The logged in user is not authorized to register this app.",
        ):
            await business_logic.register_app(
                generic_mock,
                api_port_mock,
                generic_mock,
                generic_mock,
                generic_mock,
                generic_mock,
                generic_mock,
                authz_mock,
                authc_mock,
                request,
            )

    @pytest.mark.asyncio
    async def test_edit_app_unauthorized_error(self, mocker):
        api_request_mock = mocker.MagicMock()
        persistence_mock = mocker.AsyncMock()
        api_port_mock = mocker.AsyncMock()
        api_port_mock.to_app_edit.return_value = (mocker.Mock(), None)
        api_port_mock.transform_exception = transform_exception_identity
        authz_mock = mocker.AsyncMock()
        authz_mock.authorize_operation = mocker.AsyncMock(return_value={"test": False})
        authc_mock = mocker.AsyncMock()
        request = mocker.Mock()
        with pytest.raises(
            UnauthorizedError,
            match="The logged in user is not authorized to edit this app.",
        ):
            await business_logic.edit_app(
                api_request_mock,
                api_port_mock,
                persistence_mock,
                authc_mock,
                authz_mock,
                request,
            )

    @pytest.mark.asyncio
    async def test_edit_app_success(self, mocker):
        api_request_mock = mocker.MagicMock()
        query_mock = mocker.Mock()
        query_mock.name = "test_app"
        changed_data = {"display_name": "Updated Display Name"}
        old_app_mock = mocker.Mock()
        updated_app_mock = mocker.Mock()
        expected_response = mocker.Mock()

        persistence_mock = mocker.AsyncMock()
        persistence_mock.read_one.return_value = old_app_mock
        persistence_mock.update.return_value = updated_app_mock

        api_port_mock = mocker.AsyncMock()
        api_port_mock.to_app_edit.return_value = (query_mock, changed_data)
        api_port_mock.to_api_edit_response.return_value = expected_response
        api_port_mock.transform_exception = transform_exception_identity

        authz_mock = mocker.AsyncMock()
        authz_mock.authorize_operation = mocker.AsyncMock(
            return_value={"test_app": True}
        )
        authc_mock = mocker.AsyncMock()
        authc_mock.get_actor_identifier.return_value = "test_actor"
        request = mocker.Mock()

        result = await business_logic.edit_app(
            api_request_mock,
            api_port_mock,
            persistence_mock,
            authc_mock,
            authz_mock,
            request,
        )

        assert result == expected_response
        persistence_mock.read_one.assert_called_once_with(query_mock)
        persistence_mock.update.assert_called_once_with(old_app_mock)
        api_port_mock.to_api_edit_response.assert_called_once_with(updated_app_mock)
        assert old_app_mock.display_name == "Updated Display Name"

    @pytest.mark.asyncio
    async def test_get_capability_unauthorized_error(self, mocker):
        api_request_mock = mocker.MagicMock()
        api_port_mock = mocker.AsyncMock()
        api_port_mock.transform_exception = transform_exception_identity
        persistence_mock = mocker.AsyncMock()
        authz_mock = mocker.AsyncMock()
        authz_mock.authorize_operation = mocker.AsyncMock(return_value={"test": False})
        authc_mock = mocker.AsyncMock()
        request = mocker.Mock()
        with pytest.raises(
            UnauthorizedError,
            match="The logged in user is not authorized to read this capability.",
        ):
            await business_logic.get_capability(
                api_request_mock,
                api_port_mock,
                persistence_mock,
                authc_mock,
                authz_mock,
                request,
            )

    @pytest.mark.asyncio
    async def test_get_capabilities_unauthorized_error(self, mocker):
        api_request_mock = mocker.MagicMock()
        api_port_mock = mocker.AsyncMock()
        api_port_mock.transform_exception = transform_exception_identity
        persistence_mock = mocker.AsyncMock()
        authz_mock = mocker.AsyncMock()
        authz_mock.authorize_operation = mocker.AsyncMock(return_value={"test": False})
        authc_mock = mocker.AsyncMock()
        request = mocker.Mock()
        await business_logic.get_capabilities(
            api_request_mock,
            api_port_mock,
            persistence_mock,
            authc_mock,
            authz_mock,
            request,
        )
        assert api_port_mock.to_api_get_multiple_response.call_args.args[0] == []

    @pytest.mark.asyncio
    async def test_create_capability_unauthorized_error(self, mocker):
        api_request_mock = mocker.MagicMock()
        persistence_mock = mocker.AsyncMock()
        api_port_mock = mocker.AsyncMock()
        api_port_mock.to_capability.return_value = (None, None)
        api_port_mock.transform_exception = transform_exception_identity
        bundle_server_mock = mocker.AsyncMock()
        authz_mock = mocker.AsyncMock()
        authz_mock.authorize_operation = mocker.AsyncMock(return_value={"test": False})
        authc_mock = mocker.AsyncMock()
        request = mocker.Mock()
        with pytest.raises(
            UnauthorizedError,
            match="The logged in user is not authorized to create this capability.",
        ):
            await business_logic.create_capability(
                api_request_mock,
                api_port_mock,
                bundle_server_mock,
                persistence_mock,
                authc_mock,
                authz_mock,
                request,
            )

    @pytest.mark.asyncio
    async def test_update_capability_unauthorized_error(self, mocker):
        api_request_mock = mocker.MagicMock()
        persistence_mock = mocker.AsyncMock()
        api_port_mock = mocker.AsyncMock()
        api_port_mock.to_capability.return_value = (None, None)
        api_port_mock.transform_exception = transform_exception_identity
        bundle_server_mock = mocker.AsyncMock()
        authz_mock = mocker.AsyncMock()
        authz_mock.authorize_operation = mocker.AsyncMock(return_value={"test": False})
        authc_mock = mocker.AsyncMock()
        request = mocker.Mock()
        with pytest.raises(
            UnauthorizedError,
            match="The logged in user is not authorized to update this capability.",
        ):
            await business_logic.update_capability(
                api_request_mock,
                api_port_mock,
                bundle_server_mock,
                persistence_mock,
                authc_mock,
                authz_mock,
                request,
            )

    @pytest.mark.asyncio
    async def test_delete_capability_unauthorized_error(self, mocker):
        api_request_mock = mocker.MagicMock()
        persistence_mock = mocker.AsyncMock()
        api_port_mock = mocker.AsyncMock()
        api_port_mock.to_capability.return_value = (None, None)
        api_port_mock.transform_exception = transform_exception_identity
        bundle_server_mock = mocker.AsyncMock()
        authz_mock = mocker.AsyncMock()
        authz_mock.authorize_operation = mocker.AsyncMock(return_value={"test": False})
        authc_mock = mocker.AsyncMock()
        request = mocker.Mock()
        with pytest.raises(
            UnauthorizedError,
            match="The logged in user is not authorized to delete this capability.",
        ):
            await business_logic.delete_capability(
                api_request_mock,
                api_port_mock,
                bundle_server_mock,
                persistence_mock,
                authc_mock,
                authz_mock,
                request,
            )

    @pytest.mark.asyncio
    async def test_get_namespace_unauthorized_error(self, mocker):
        api_request_mock = mocker.MagicMock()
        api_port_mock = mocker.AsyncMock()
        api_port_mock.transform_exception = transform_exception_identity
        persistence_mock = mocker.AsyncMock()
        persistence_mock.read_one = mocker.AsyncMock(return_value={"test": "test"})
        authz_mock = mocker.AsyncMock()
        authz_mock.authorize_operation = mocker.AsyncMock(return_value={"test": False})
        authc_mock = mocker.AsyncMock()
        request = mocker.Mock()
        with pytest.raises(
            UnauthorizedError,
            match="The logged in user is not authorized to read this namespace.",
        ):
            await business_logic.get_namespace(
                api_request_mock,
                api_port_mock,
                persistence_mock,
                authc_mock,
                authz_mock,
                request,
            )

    @pytest.mark.asyncio
    async def test_get_namespaces_unauthorized(self, mocker):
        api_request_mock = mocker.MagicMock()
        api_port_mock = mocker.AsyncMock()
        api_port_mock.transform_exception = transform_exception_identity
        persistence_mock = mocker.AsyncMock()
        authz_mock = mocker.AsyncMock()
        authz_mock.authorize_operation = mocker.AsyncMock(return_value={"test": False})
        authc_mock = mocker.AsyncMock()
        request = mocker.Mock()
        await business_logic.get_namespaces(
            api_request_mock,
            api_port_mock,
            persistence_mock,
            authc_mock,
            authz_mock,
            request,
        )
        assert (
            api_port_mock.to_api_namespaces_get_response.call_args.kwargs["namespaces"]
            == []
        )

    @pytest.mark.asyncio
    async def test_create_namespace_unauthorized_error(self, mocker):
        api_request_mock = mocker.MagicMock()
        persistence_mock = mocker.AsyncMock()
        api_port_mock = mocker.AsyncMock()
        api_port_mock.to_namespace.return_value = (None, None)
        api_port_mock.transform_exception = transform_exception_identity
        authz_mock = mocker.AsyncMock()
        authz_mock.authorize_operation = mocker.AsyncMock(return_value={"test": False})
        authc_mock = mocker.AsyncMock()
        request = mocker.Mock()
        with pytest.raises(
            UnauthorizedError,
            match="The logged in user is not authorized to create this namespace.",
        ):
            await business_logic.create_namespace(
                api_request_mock,
                api_port_mock,
                persistence_mock,
                authc_mock,
                authz_mock,
                request,
            )

    @pytest.mark.asyncio
    async def test_edit_namespace_unauthorized_error(self, mocker):
        api_request_mock = mocker.MagicMock()
        persistence_mock = mocker.AsyncMock()
        api_port_mock = mocker.AsyncMock()
        api_port_mock.to_namespace.return_value = (None, None)
        api_port_mock.transform_exception = transform_exception_identity
        authz_mock = mocker.AsyncMock()
        authz_mock.authorize_operation = mocker.AsyncMock(return_value={"test": False})
        authc_mock = mocker.AsyncMock()
        request = mocker.Mock()
        with pytest.raises(
            UnauthorizedError,
            match="The logged in user is not authorized to update this namespace.",
        ):
            await business_logic.edit_namespace(
                api_request_mock,
                api_port_mock,
                persistence_mock,
                authc_mock,
                authz_mock,
                request,
            )

    @pytest.mark.asyncio
    async def test_get_role_unauthorized_error(self, mocker):
        api_request_mock = mocker.MagicMock()
        api_port_mock = mocker.AsyncMock()
        api_port_mock.transform_exception = transform_exception_identity
        persistence_mock = mocker.AsyncMock()
        persistence_mock.read_one = mocker.AsyncMock(return_value={"test": "test"})
        authz_mock = mocker.AsyncMock()
        authz_mock.authorize_operation = mocker.AsyncMock(return_value={"test": False})
        authc_mock = mocker.AsyncMock()
        request_mock = mocker.Mock()
        with pytest.raises(
            UnauthorizedError,
            match="The logged in user is not authorized to read this role.",
        ):
            await business_logic.get_role(
                api_request_mock,
                api_port_mock,
                persistence_mock,
                authc_mock,
                authz_mock,
                request_mock,
            )

    @pytest.mark.asyncio
    async def test_get_roles_unauthorized(self, mocker):
        api_request_mock = mocker.MagicMock()
        api_port_mock = mocker.AsyncMock()
        api_port_mock.transform_exception = transform_exception_identity
        persistence_mock = mocker.AsyncMock()
        authz_mock = mocker.AsyncMock()
        authz_mock.authorize_operation = mocker.AsyncMock(return_value={"test": False})
        authc_mock = mocker.AsyncMock()
        request_mock = mocker.Mock()
        await business_logic.get_roles(
            api_request_mock,
            api_port_mock,
            persistence_mock,
            authc_mock,
            authz_mock,
            request_mock,
        )
        assert api_port_mock.to_roles_get_response.call_args.kwargs["roles"] == []

    @pytest.mark.asyncio
    async def test_create_role_unauthorized_error(self, mocker):
        api_request_mock = mocker.MagicMock()
        persistence_mock = mocker.AsyncMock()
        api_port_mock = mocker.AsyncMock()
        api_port_mock.to_role.return_value = (None, None)
        api_port_mock.transform_exception = transform_exception_identity
        authz_mock = mocker.AsyncMock()
        authz_mock.authorize_operation = mocker.AsyncMock(return_value={})
        authc_mock = mocker.AsyncMock()
        request_mock = mocker.Mock()
        with pytest.raises(
            UnauthorizedError,
            match="The logged in user is not authorized to create this role.",
        ):
            await business_logic.create_role(
                api_request_mock,
                api_port_mock,
                persistence_mock,
                authc_mock,
                authz_mock,
                request_mock,
            )

    @pytest.mark.asyncio
    async def test_edit_role_unauthorized_error(self, mocker):
        api_request_mock = mocker.MagicMock()
        persistence_mock = mocker.AsyncMock()
        api_port_mock = mocker.AsyncMock()
        api_port_mock.to_role.return_value = (None, None)
        api_port_mock.transform_exception = transform_exception_identity
        authz_mock = mocker.AsyncMock()
        authz_mock.authorize_operation = mocker.AsyncMock(return_value={})
        authc_mock = mocker.AsyncMock()
        request_mock = mocker.Mock()
        with pytest.raises(
            UnauthorizedError,
            match="The logged in user is not authorized to edit this role.",
        ):
            await business_logic.edit_role(
                api_request_mock,
                api_port_mock,
                persistence_mock,
                authc_mock,
                authz_mock,
                request_mock,
            )

    @pytest.mark.asyncio
    async def test_get_condition_unauthorized_error(self, mocker):
        api_request_mock = mocker.MagicMock()
        api_port_mock = mocker.AsyncMock()
        api_port_mock.transform_exception = transform_exception_identity
        persistence_mock = mocker.AsyncMock()
        persistence_mock.read_one = mocker.AsyncMock(return_value={"test": "test"})
        authz_mock = mocker.AsyncMock()
        authz_mock.authorize_operation = mocker.AsyncMock(return_value={})
        authc_mock = mocker.AsyncMock()
        request_mock = mocker.Mock()
        with pytest.raises(
            UnauthorizedError,
            match="The logged in user is not authorized to read this condition.",
        ):
            await business_logic.get_condition(
                api_request_mock,
                api_port_mock,
                persistence_mock,
                authc_mock,
                authz_mock,
                request_mock,
            )

    @pytest.mark.asyncio
    async def test_get_conditions_unauthorized(self, mocker):
        api_request_mock = mocker.MagicMock()
        api_port_mock = mocker.AsyncMock()
        api_port_mock.transform_exception = transform_exception_identity
        persistence_mock = mocker.AsyncMock()
        authz_mock = mocker.AsyncMock()
        authz_mock.authorize_operation = mocker.AsyncMock(return_value={})
        authc_mock = mocker.AsyncMock()
        request_mock = mocker.Mock()
        await business_logic.get_conditions(
            api_request_mock,
            api_port_mock,
            persistence_mock,
            authc_mock,
            authz_mock,
            request_mock,
        )
        assert api_port_mock.to_api_get_multiple_response.call_args.args[0] == []

    @pytest.mark.asyncio
    async def test_create_condition_unauthorized_error(self, mocker):
        api_request_mock = mocker.MagicMock()
        persistence_mock = mocker.AsyncMock()
        api_port_mock = mocker.AsyncMock()
        api_port_mock.transform_exception = transform_exception_identity
        bundle_server_mock = mocker.AsyncMock()
        authz_mock = mocker.AsyncMock()
        authz_mock.authorize_operation = mocker.AsyncMock(return_value={})
        authc_mock = mocker.AsyncMock()
        request_mock = mocker.Mock()
        with pytest.raises(
            UnauthorizedError,
            match="The logged in user is not authorized to create this condition.",
        ):
            await business_logic.create_condition(
                api_request_mock,
                api_port_mock,
                bundle_server_mock,
                persistence_mock,
                authc_mock,
                authz_mock,
                request_mock,
            )

    @pytest.mark.asyncio
    async def test_update_condition_unauthorized_error(self, mocker):
        api_request_mock = mocker.MagicMock()
        persistence_mock = mocker.AsyncMock()
        api_port_mock = mocker.AsyncMock()
        api_port_mock.to_obj_edit.return_value = (mocker.Mock(), None)
        api_port_mock.transform_exception = transform_exception_identity
        bundle_server_mock = mocker.AsyncMock()
        authz_mock = mocker.AsyncMock()
        authz_mock.authorize_operation = mocker.AsyncMock(return_value={})
        authc_mock = mocker.AsyncMock()
        request_mock = mocker.Mock()
        with pytest.raises(
            UnauthorizedError,
            match="The logged in user is not authorized to update this condition.",
        ):
            await business_logic.update_condition(
                api_request_mock,
                api_port_mock,
                bundle_server_mock,
                persistence_mock,
                authc_mock,
                authz_mock,
                request_mock,
            )

    @pytest.mark.asyncio
    async def test_get_permission_unauthorized_error(self, mocker):
        api_request_mock = mocker.MagicMock()
        api_port_mock = mocker.AsyncMock()
        api_port_mock.transform_exception = transform_exception_identity
        persistence_mock = mocker.AsyncMock()
        persistence_mock.read_one = mocker.AsyncMock(return_value={"test": "test"})
        authz_mock = mocker.AsyncMock()
        authz_mock.authorize_operation = mocker.AsyncMock(return_value={})
        authc_mock = mocker.AsyncMock()
        request_mock = mocker.Mock()
        with pytest.raises(
            UnauthorizedError,
            match="The logged in user is not authorized to read this permission.",
        ):
            await business_logic.get_permission(
                api_request_mock,
                api_port_mock,
                persistence_mock,
                authc_mock,
                authz_mock,
                request_mock,
            )

    @pytest.mark.asyncio
    async def test_get_permissions_unauthorized(self, mocker):
        api_request_mock = mocker.MagicMock()
        api_port_mock = mocker.AsyncMock()
        api_port_mock.transform_exception = transform_exception_identity
        persistence_mock = mocker.AsyncMock()
        authz_mock = mocker.AsyncMock()
        authz_mock.authorize_operation = mocker.AsyncMock(return_value={})
        authc_mock = mocker.AsyncMock()
        request_mock = mocker.Mock()
        await business_logic.get_permissions(
            api_request_mock,
            api_port_mock,
            persistence_mock,
            authc_mock,
            authz_mock,
            request_mock,
        )
        assert api_port_mock.to_api_get_multiple_response.call_args.args[0] == []

    @pytest.mark.asyncio
    async def test_create_permission_unauthorized_error(self, mocker):
        api_request_mock = mocker.MagicMock()
        persistence_mock = mocker.AsyncMock()
        api_port_mock = mocker.AsyncMock()
        api_port_mock.transform_exception = transform_exception_identity
        authz_mock = mocker.AsyncMock()
        authz_mock.authorize_operation = mocker.AsyncMock(return_value={})
        authc_mock = mocker.AsyncMock()
        request_mock = mocker.Mock()
        with pytest.raises(
            UnauthorizedError,
            match="The logged in user is not authorized to create this permission.",
        ):
            await business_logic.create_permission(
                api_request_mock,
                api_port_mock,
                persistence_mock,
                authc_mock,
                authz_mock,
                request_mock,
            )

    @pytest.mark.asyncio
    async def test_edit_permission_unauthorized_error(self, mocker):
        api_request_mock = mocker.MagicMock()
        persistence_mock = mocker.AsyncMock()
        api_port_mock = mocker.AsyncMock()
        api_port_mock.to_obj_edit.return_value = (mocker.Mock(), None)
        api_port_mock.transform_exception = transform_exception_identity
        authz_mock = mocker.AsyncMock()
        authz_mock.authorize_operation = mocker.AsyncMock(return_value={})
        authc_mock = mocker.AsyncMock()
        request_mock = mocker.Mock()
        with pytest.raises(
            UnauthorizedError,
            match="The logged in user is not authorized to edit this permission.",
        ):
            await business_logic.edit_permission(
                api_request_mock,
                api_port_mock,
                persistence_mock,
                authc_mock,
                authz_mock,
                request_mock,
            )

    @pytest.mark.asyncio
    async def test_get_context_unauthorized_error(self, mocker):
        api_request_mock = mocker.MagicMock()
        persistence_mock = mocker.AsyncMock()
        persistence_mock.read_one = mocker.AsyncMock(return_value={"test": "test"})
        api_port_mock = mocker.AsyncMock()
        api_port_mock.transform_exception = transform_exception_identity
        authz_mock = mocker.AsyncMock()
        authz_mock.authorize_operation = mocker.AsyncMock(return_value={})
        authc_mock = mocker.AsyncMock()
        request_mock = mocker.Mock()
        with pytest.raises(
            UnauthorizedError,
            match="The logged in user is not authorized to read this context.",
        ):
            await business_logic.get_context(
                api_request_mock,
                api_port_mock,
                persistence_mock,
                authc_mock,
                authz_mock,
                request_mock,
            )

    @pytest.mark.asyncio
    async def test_get_contexts_unauthorized(self, mocker):
        api_request_mock = mocker.MagicMock()
        api_port_mock = mocker.AsyncMock()
        api_port_mock.transform_exception = transform_exception_identity
        persistence_mock = mocker.AsyncMock()
        authz_mock = mocker.AsyncMock()
        authz_mock.authorize_operation = mocker.AsyncMock(return_value={})
        authc_mock = mocker.AsyncMock()
        request_mock = mocker.Mock()
        await business_logic.get_contexts(
            api_request_mock,
            api_port_mock,
            persistence_mock,
            authc_mock,
            authz_mock,
            request_mock,
        )
        assert api_port_mock.to_api_contexts_get_response.call_args.args[0] == []

    @pytest.mark.asyncio
    async def test_create_context_unauthorized_error(self, mocker):
        api_request_mock = mocker.MagicMock()
        persistence_mock = mocker.AsyncMock()
        api_port_mock = mocker.AsyncMock()
        api_port_mock.transform_exception = transform_exception_identity
        authz_mock = mocker.AsyncMock()
        authz_mock.authorize_operation = mocker.AsyncMock(return_value={})
        authc_mock = mocker.AsyncMock()
        request_mock = mocker.Mock()
        with pytest.raises(
            UnauthorizedError,
            match="The logged in user is not authorized to create this context.",
        ):
            await business_logic.create_context(
                api_request_mock,
                persistence_mock,
                api_port_mock,
                authc_mock,
                authz_mock,
                request_mock,
            )

    @pytest.mark.asyncio
    async def test_edit_context_unauthorized_error(self, mocker):
        api_request_mock = mocker.MagicMock()
        persistence_mock = mocker.AsyncMock()
        api_port_mock = mocker.AsyncMock()
        api_port_mock.to_context_edit.return_value = (mocker.Mock(), None)
        api_port_mock.transform_exception = transform_exception_identity
        authz_mock = mocker.AsyncMock()
        authz_mock.authorize_operation = mocker.AsyncMock(return_value={})
        authc_mock = mocker.AsyncMock()
        request_mock = mocker.Mock()
        with pytest.raises(
            UnauthorizedError,
            match="The logged in user is not authorized to edit this context.",
        ):
            await business_logic.edit_context(
                api_request_mock,
                api_port_mock,
                persistence_mock,
                authc_mock,
                authz_mock,
                request_mock,
            )


DELETE_FN_CONFIGS = [
    {
        "id": "condition",
        "fn": business_logic.delete_condition,
        "api_port_method": "to_obj_get_single",
        "resource_type": ResourceType.CONDITION,
        "name": "cond",
        "namespace_name": "ns",
        "app_name": "app",
        "has_dependencies_check": True,
        "builtin_msg": "This condition cannot be deleted because it is a built-in condition.",
        "unauthorized_msg": "The logged in user is not authorized to delete this condition.",
        "uses_bundle_server": True,
    },
    {
        "id": "permission",
        "fn": business_logic.delete_permission,
        "api_port_method": "to_obj_get_single",
        "resource_type": ResourceType.PERMISSION,
        "name": "perm",
        "namespace_name": "ns",
        "app_name": "app",
        "has_dependencies_check": True,
        "builtin_msg": "This permission cannot be deleted because it is a built-in permission.",
        "unauthorized_msg": "The logged in user is not authorized to delete this permission.",
        "uses_bundle_server": True,
    },
    {
        "id": "capability",
        "fn": business_logic.delete_capability,
        "api_port_method": "to_obj_get_single",
        "resource_type": ResourceType.CAPABILITY,
        "name": "cap",
        "namespace_name": "ns",
        "app_name": "app",
        "has_dependencies_check": True,
        "builtin_msg": "This capability cannot be deleted because it is a built-in capability.",
        "unauthorized_msg": "The logged in user is not authorized to delete this capability.",
        "uses_bundle_server": True,
    },
    {
        "id": "context",
        "fn": business_logic.delete_context,
        "api_port_method": "to_context_get",
        "resource_type": ResourceType.CONTEXT,
        "name": "ctx",
        "namespace_name": None,
        "app_name": "app",
        "has_dependencies_check": False,
        "builtin_msg": "This context cannot be deleted because it is a built-in context.",
        "unauthorized_msg": "The logged in user is not authorized to delete this context.",
        "uses_bundle_server": True,
    },
    {
        "id": "role",
        "fn": business_logic.delete_role,
        "api_port_method": "to_role_get",
        "resource_type": ResourceType.ROLE,
        "name": "role",
        "namespace_name": None,
        "app_name": "app",
        "has_dependencies_check": True,
        "builtin_msg": "This role cannot be deleted because it is a built-in role.",
        "unauthorized_msg": "The logged in user is not authorized to delete this role.",
        "uses_bundle_server": True,
    },
    {
        "id": "app",
        "fn": business_logic.delete_app,
        "api_port_method": "to_app_get",
        "resource_type": ResourceType.APP,
        "name": "guardian",
        "namespace_name": None,
        "app_name": None,
        "has_dependencies_check": True,
        "builtin_msg": "This app cannot be deleted because it is a built-in app.",
        "unauthorized_msg": "The logged in user is not authorized to delete this app.",
        "uses_bundle_server": True,
    },
    {
        "id": "namespace",
        "fn": business_logic.delete_namespace,
        "api_port_method": "to_namespace_get",
        "resource_type": ResourceType.NAMESPACE,
        "name": "builtin",
        "namespace_name": None,
        "app_name": "guardian",
        "has_dependencies_check": True,
        "builtin_msg": "This namespace cannot be deleted because it is a built-in namespace.",
        "unauthorized_msg": "The logged in user is not authorized to delete this namespace.",
        "uses_bundle_server": True,
    },
]


def _resource_id(cfg):
    if cfg["resource_type"] == ResourceType.APP:
        return cfg["name"]
    if cfg["resource_type"] in (
        ResourceType.NAMESPACE,
        ResourceType.ROLE,
        ResourceType.CONTEXT,
    ):
        return f"{cfg['app_name']}:{cfg['name']}"
    return f"{cfg['app_name']}:{cfg['namespace_name']}:{cfg['name']}"


def _build_delete_mocks(cfg, mocker, *, is_builtin, allowed=True, dependencies=None):
    """Build the mock kwargs needed to invoke a delete_* business_logic function.

    `is_builtin` is the boolean status flag on the object returned by read_one.
    `allowed` controls the authz mock outcome.
    `dependencies` is what persistence.read_dependencies returns (default []).
    """
    persisted = mocker.Mock(spec=[])
    persisted.name = cfg["name"]
    persisted.namespace_name = cfg["namespace_name"]
    persisted.app_name = cfg["app_name"]
    persisted.is_builtin = is_builtin

    persistence_mock = mocker.AsyncMock()
    persistence_mock.read_one.return_value = persisted
    persistence_mock.read_dependencies.return_value = (
        dependencies if dependencies is not None else []
    )

    api_port_mock = mocker.AsyncMock()
    api_port_mock.transform_exception = transform_exception_identity
    getattr(api_port_mock, cfg["api_port_method"]).return_value = mocker.Mock()

    authz_mock = mocker.AsyncMock()
    authz_mock.authorize_operation = mocker.AsyncMock(
        return_value={_resource_id(cfg): allowed}
    )
    authc_mock = mocker.AsyncMock()
    authc_mock.get_actor_identifier.return_value = "actor"
    bundle_server_mock = mocker.AsyncMock()
    request_mock = mocker.Mock()

    return {
        "api_request": mocker.MagicMock(),
        "api_port": api_port_mock,
        "bundle_server": bundle_server_mock,
        "persistence": persistence_mock,
        "authc": authc_mock,
        "authz": authz_mock,
        "request": request_mock,
        "persisted": persisted,
    }


async def _invoke_delete(cfg, mocks):
    return await cfg["fn"](
        mocks["api_request"],
        mocks["api_port"],
        mocks["bundle_server"],
        mocks["persistence"],
        mocks["authc"],
        mocks["authz"],
        mocks["request"],
    )


@pytest.mark.parametrize("cfg", DELETE_FN_CONFIGS, ids=lambda c: c["id"])
class TestBuiltinFlagProtection:
    """The is_builtin flag prevents deletion across every delete_* business_logic function."""

    @pytest.mark.asyncio
    async def test_delete_proceeds_when_not_builtin(self, cfg, mocker):
        mocks = _build_delete_mocks(cfg, mocker, is_builtin=False)
        result = await _invoke_delete(cfg, mocks)
        assert result is None
        mocks["persistence"].delete.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_delete_blocked_when_builtin(self, cfg, mocker):
        mocks = _build_delete_mocks(cfg, mocker, is_builtin=True)
        with pytest.raises(DependencyExistsError, match=cfg["builtin_msg"]):
            await _invoke_delete(cfg, mocks)
        mocks["persistence"].delete.assert_not_called()

    @pytest.mark.asyncio
    async def test_unauthorized_takes_precedence_over_builtin(self, cfg, mocker):
        mocks = _build_delete_mocks(cfg, mocker, is_builtin=True, allowed=False)
        with pytest.raises(UnauthorizedError, match=cfg["unauthorized_msg"]):
            await _invoke_delete(cfg, mocks)
        mocks["persistence"].delete.assert_not_called()

    @pytest.mark.asyncio
    async def test_builtin_takes_precedence_over_dependencies(self, cfg, mocker):
        if not cfg["has_dependencies_check"]:
            pytest.skip(f"{cfg['id']} delete does not check dependencies")
        mocks = _build_delete_mocks(
            cfg,
            mocker,
            is_builtin=True,
            dependencies=[mocker.Mock(), mocker.Mock()],
        )
        with pytest.raises(DependencyExistsError, match=cfg["builtin_msg"]):
            await _invoke_delete(cfg, mocks)
        mocks["persistence"].delete.assert_not_called()
