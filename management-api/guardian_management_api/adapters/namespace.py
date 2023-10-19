# Copyright (C) 2023 Univention GmbH
#
# SPDX-License-Identifier: AGPL-3.0-only

from dataclasses import asdict
from typing import List, Optional, Type

from port_loader import AsyncConfiguredAdapterMixin

from ..constants import COMPLETE_URL
from ..errors import ObjectNotFoundError, ParentNotFoundError
from ..models.base import PaginationRequest, PersistenceGetManyResult
from ..models.namespace import (
    Namespace,
    NamespaceCreateQuery,
    NamespaceEditQuery,
    NamespaceGetQuery,
    NamespacesGetQuery,
)
from ..models.routers.base import GetByAppRequest, PaginationInfo
from ..models.routers.namespace import (
    Namespace as ResponseNamespace,
)
from ..models.routers.namespace import (
    NamespaceCreateRequest,
    NamespaceEditRequest,
    NamespaceGetRequest,
    NamespaceMultipleResponse,
    NamespacesGetRequest,
    NamespaceSingleResponse,
)
from ..models.sql_persistence import DBApp, DBNamespace, SQLPersistenceAdapterSettings
from ..ports.namespace import (
    NamespaceAPIEditRequestObject,
    NamespaceAPIPort,
    NamespacePersistencePort,
)
from .fastapi_utils import TransformExceptionMixin
from .sql_persistence import SQLAlchemyMixin


class TransformNamespaceExceptionMixin(TransformExceptionMixin):
    ...


class FastAPINamespaceAPIAdapter(
    TransformNamespaceExceptionMixin,
    NamespaceAPIPort[
        NamespaceCreateRequest,
        NamespaceSingleResponse,
        NamespaceGetRequest,
        NamespaceSingleResponse,
        NamespacesGetRequest,
        NamespaceMultipleResponse,
        NamespaceAPIEditRequestObject,
        NamespaceSingleResponse,
        GetByAppRequest,
        NamespaceMultipleResponse,
    ],
):
    async def to_namespaces_by_appname_get(
        self, api_request: GetByAppRequest
    ) -> NamespacesGetQuery:
        return NamespacesGetQuery(
            pagination=PaginationRequest(
                query_offset=api_request.offset,
                query_limit=api_request.limit,
            ),
            app_name=api_request.app_name,
        )

    async def to_api_edit_response(
        self, namespace_result: Namespace
    ) -> NamespaceSingleResponse:
        return NamespaceSingleResponse(
            namespace=ResponseNamespace(
                name=namespace_result.name,
                app_name=namespace_result.app_name,
                display_name=namespace_result.display_name,
                resource_url=f"{COMPLETE_URL}/namespaces/{namespace_result.app_name}/{namespace_result.name}",
            )
        )

    async def to_namespace_edit(
        self,
        api_request: NamespaceEditRequest,
    ) -> NamespaceEditQuery:
        return NamespaceEditQuery(
            name=api_request.name,
            display_name=api_request.data.display_name,
            app_name=api_request.app_name,
        )

    class Config:
        alias = "fastapi"

    async def to_namespace_create(
        self, api_request: NamespaceCreateRequest
    ) -> NamespaceCreateQuery:
        return NamespaceCreateQuery(
            name=api_request.data.name,
            display_name=api_request.data.display_name,
            app_name=api_request.app_name,
        )

    async def to_api_create_response(
        self, namespace_result: Namespace
    ) -> NamespaceSingleResponse:
        return NamespaceSingleResponse(
            namespace=ResponseNamespace(
                name=namespace_result.name,
                app_name=namespace_result.app_name,
                display_name=namespace_result.display_name,
                resource_url=f"{COMPLETE_URL}/namespaces/{namespace_result.app_name}/{namespace_result.name}",
            )
        )

    async def to_api_get_response(
        self, namespace_result: Namespace
    ) -> NamespaceSingleResponse:
        return NamespaceSingleResponse(
            namespace=ResponseNamespace(
                name=namespace_result.name,
                app_name=namespace_result.app_name,
                display_name=namespace_result.display_name,
                resource_url=f"{COMPLETE_URL}/namespaces/{namespace_result.app_name}/{namespace_result.name}",
            )
        )

    async def to_namespace_get(
        self, api_request: NamespaceGetRequest
    ) -> NamespaceGetQuery:
        return NamespaceGetQuery(
            name=api_request.name,
            app_name=api_request.app_name,
        )

    async def to_namespaces_get(
        self, api_request: NamespacesGetRequest
    ) -> NamespacesGetQuery:
        return NamespacesGetQuery(
            pagination=PaginationRequest(
                query_offset=api_request.offset,
                query_limit=api_request.limit,
            )
        )

    async def to_api_namespaces_get_response(
        self,
        namespaces: List[Namespace],
        query_offset: int,
        query_limit: Optional[int],
        total_count: int,
    ) -> NamespaceMultipleResponse:
        return NamespaceMultipleResponse(
            pagination=PaginationInfo(
                offset=query_offset,
                limit=query_limit,
                total_count=total_count,
            ),
            namespaces=[
                ResponseNamespace(
                    name=ns.name,
                    display_name=ns.display_name,
                    app_name=ns.app_name,
                    resource_url=f"http://localhost:8001/guardian/management/namespaces/{ns.app_name}/{ns.name}",
                )
                for ns in namespaces
            ],
        )


class SQLNamespacePersistenceAdapter(
    AsyncConfiguredAdapterMixin, NamespacePersistencePort, SQLAlchemyMixin
):
    @staticmethod
    def _namespace_to_db_namespace(namespace: Namespace, app_id: int) -> DBNamespace:
        return DBNamespace(
            app_id=app_id, name=namespace.name, display_name=namespace.display_name
        )

    @staticmethod
    def _db_namespace_to_namespace(db_namespace: DBNamespace) -> Namespace:
        return Namespace(
            name=db_namespace.name,
            display_name=db_namespace.display_name,
            app_name=db_namespace.app.name,
        )

    class Config:
        alias = "sql"
        cached = True

    @classmethod
    def get_settings_cls(
        cls,
    ) -> Type[SQLPersistenceAdapterSettings]:  # pragma: no cover
        return SQLPersistenceAdapterSettings

    async def configure(self, settings: SQLPersistenceAdapterSettings):
        self._db_string = SQLAlchemyMixin.create_db_string(**asdict(settings))

    async def create(self, namespace: Namespace) -> Namespace:
        db_app = await self._get_single_object(DBApp, name=namespace.app_name)
        if db_app is None:
            raise ParentNotFoundError(
                "The app/namespace of the object to be created does not exist."
            )
        async with self.session() as session:
            db_ns = SQLNamespacePersistenceAdapter._namespace_to_db_namespace(
                namespace, db_app.id
            )
            result = await self._create_object(db_ns, session=session)
        return SQLNamespacePersistenceAdapter._db_namespace_to_namespace(result)

    async def read_one(self, query: NamespaceGetQuery) -> Namespace:
        result = await self._get_single_object(
            DBNamespace, name=query.name, app_name=query.app_name
        )
        if result is None:
            raise ObjectNotFoundError(
                f"No namespace with the identifier '{query.app_name}:"
                f"{query.name}' could be found."
            )
        return SQLNamespacePersistenceAdapter._db_namespace_to_namespace(result)

    async def read_many(
        self,
        query: NamespacesGetQuery,
    ) -> PersistenceGetManyResult[Namespace]:
        dp_namespaces, total_count = await self._get_many_objects(
            DBNamespace,
            query.pagination.query_offset,
            query.pagination.query_limit,
            app_name=query.app_name,
        )
        namespaces = [
            SQLNamespacePersistenceAdapter._db_namespace_to_namespace(db_app)
            for db_app in dp_namespaces
        ]
        return PersistenceGetManyResult(total_count=total_count, objects=namespaces)

    async def update(self, namespace: Namespace) -> Namespace:
        db_app = await self._get_single_object(
            DBNamespace, name=namespace.name, app_name=namespace.app_name
        )
        if db_app is None:
            raise ObjectNotFoundError(
                f"No app with the identifier '{namespace.app_name}:{namespace.name}' could be found."
            )
        modified = await self._update_object(
            db_app, display_name=namespace.display_name
        )
        return SQLNamespacePersistenceAdapter._db_namespace_to_namespace(modified)
