# Copyright (C) 2023 Univention GmbH
#
# SPDX-License-Identifier: AGPL-3.0-only
import pytest
import pytest_asyncio
from guardian_management_api.adapters.permission import (
    FastAPIPermissionAPIAdapter,
    PermissionStaticDataAdapter,
)
from guardian_management_api.constants import COMPLETE_URL
from guardian_management_api.models.permission import (
    Permission,
    PermissionCreateQuery,
    PermissionGetQuery,
)
from guardian_management_api.models.routers.permission import (
    FastAPIPermission,
    PermissionCreateData,
    PermissionCreateRequest,
    PermissionEditData,
    PermissionEditRequest,
    PermissionGetRequest,
    PermissionSingleResponse,
)
from guardian_management_api.ports.permission import PermissionAPIPort


class TestFastPermissionAppAdapter:
    @pytest_asyncio.fixture
    async def adapter(self, registry_test_adapters) -> FastAPIPermissionAPIAdapter:
        return await registry_test_adapters.request_port(PermissionAPIPort)

    @pytest.mark.asyncio
    async def test_to_permission_create(self, adapter):
        app_name = "app_name_1"
        namespace_name = "namespace_name_1"
        name = "name_1"
        display_name = "display_name_1"

        api_request = PermissionCreateRequest(
            data=PermissionCreateData(
                name=name,
                display_name=display_name,
            ),
            namespace_name=namespace_name,
            app_name=app_name,
        )

        result = await adapter.to_obj_create(api_request)
        assert result == PermissionCreateQuery(
            permissions=[
                Permission(
                    name=name,
                    display_name=display_name,
                    app_name=app_name,
                    namespace_name=namespace_name,
                )
            ],
        )

    @pytest.mark.asyncio
    async def test_to_api_create_response(self, adapter):
        name = "name_2"
        display_name = "display_name_2"
        app_name = "app_name_2"
        namespace_name = "namespace_name_2"

        permission = Permission(
            name=name,
            display_name=display_name,
            app_name=app_name,
            namespace_name=namespace_name,
        )

        result = await adapter.to_api_get_single_response(permission)
        assert result == PermissionSingleResponse(
            permission=FastAPIPermission(
                name=name,
                display_name=display_name,
                app_name=app_name,
                namespace_name=namespace_name,
                resource_url=f"{COMPLETE_URL}/permissions/{app_name}/{namespace_name}/{name}",
            )
        )

    @pytest.mark.asyncio
    async def test_to_permission_get(self, adapter):
        name = "name_3"
        app_name = "app_name_3"
        namespace_name = "namespace_name_3"

        api_request = PermissionGetRequest(
            name=name,
            app_name=app_name,
            namespace_name=namespace_name,
        )

        result = await adapter.to_obj_get_single(api_request)
        assert result == PermissionGetQuery(
            name=name, app_name=app_name, namespace_name=namespace_name
        )

    @pytest.mark.asyncio
    async def test_to_api_get_response(self, adapter):
        name = "name_4"
        display_name = "display_name_4"
        app_name = "app_name_4"
        namespace_name = "namespace_name_4"

        permission = Permission(
            name=name,
            display_name=display_name,
            app_name=app_name,
            namespace_name=namespace_name,
        )

        result = await adapter.to_api_get_single_response(permission)

        assert result == PermissionSingleResponse(
            permission=FastAPIPermission(
                name=name,
                display_name=display_name,
                app_name=app_name,
                namespace_name=namespace_name,
                resource_url=f"{COMPLETE_URL}/permissions/{app_name}/{namespace_name}/{name}",
            )
        )

    @pytest.mark.asyncio
    async def test_to_permission_edit(self, adapter):
        name = "name_5"
        display_name = "display_name_5"
        app_name = "app_name_5"
        namespace_name = "namespace_name_5"

        permission_edit_request = PermissionEditRequest(
            name=name,
            app_name=app_name,
            namespace_name=namespace_name,
            data=PermissionEditData(display_name=display_name),
        )
        query, changed = await adapter.to_obj_edit(permission_edit_request)
        assert query == PermissionGetQuery(
            name=name,
            app_name=app_name,
            namespace_name=namespace_name,
        )
        assert changed == {"display_name": display_name}

    @pytest.mark.asyncio
    async def test_to_api_edit_response(self, adapter):
        name = "name_6"
        display_name = "display_name_6"
        app_name = "app_name_6"
        namespace_name = "namespace_name_6"

        permission = Permission(
            name=name,
            display_name=display_name,
            app_name=app_name,
            namespace_name=namespace_name,
        )
        result = await adapter.to_api_get_single_response(permission)
        assert result == PermissionSingleResponse(
            permission=FastAPIPermission(
                name=name,
                display_name=display_name,
                app_name=app_name,
                namespace_name=namespace_name,
                resource_url=f"{COMPLETE_URL}/permissions/{app_name}/{namespace_name}/{name}",
            )
        )


class TestPermissionStaticDataAdapter:
    @pytest.fixture(autouse=True)
    def adapter(self):
        return PermissionStaticDataAdapter()

    @pytest.mark.asyncio
    async def test_update(self, adapter):
        from guardian_management_api.errors import ObjectNotFoundError

        with pytest.raises(ObjectNotFoundError):
            await adapter.update(
                Permission(namespace_name="ns1", app_name="a", name="n")
            )
