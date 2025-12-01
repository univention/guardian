# Copyright (C) 2023 Univention GmbH
#
# SPDX-License-Identifier: AGPL-3.0-only

from dataclasses import asdict
from typing import Any, Dict, List, Optional, Tuple, Type, Union

from port_loader import AsyncConfiguredAdapterMixin

from ..constants import COMPLETE_URL
from ..errors import ObjectNotFoundError, ParentNotFoundError
from ..models.base import PaginationRequest, PersistenceGetManyResult
from ..models.context import (
    Context,
    ContextGetQuery,
    ContextsGetQuery,
)
from ..models.routers.base import (
    GetAllRequest,
    GetByAppRequest,
    GetByNamespaceRequest,
    PaginationInfo,
)
from ..models.routers.context import (
    Context as ResponseContext,
)
from ..models.routers.context import (
    ContextCreateRequest,
    ContextEditRequest,
    ContextGetRequest,
    ContextMultipleResponse,
    ContextSingleResponse,
)
from ..models.sql_persistence import (
    DBApp,
    DBContext,
    DBNamespace,
    SQLPersistenceAdapterSettings,
)
from ..ports.context import (
    ContextAPIPort,
    ContextPersistencePort,
)
from .fastapi_utils import TransformExceptionMixin
from .sql_persistence import SQLAlchemyMixin


class TransformContextExceptionMixin(TransformExceptionMixin): ...


class FastAPIContextAPIAdapter(
    TransformContextExceptionMixin,
    ContextAPIPort[
        ContextCreateRequest,
        ContextSingleResponse,
        ContextGetRequest,
        ContextSingleResponse,
        Union[GetAllRequest, GetByAppRequest, GetByNamespaceRequest],
        ContextMultipleResponse,
        Tuple[ContextGetQuery, Dict[str, Any]],
        ContextSingleResponse,
    ],
):
    class Config:
        alias = "fastapi"

    async def to_api_edit_response(
        self, context_result: Context
    ) -> ContextSingleResponse:
        return ContextSingleResponse(
            context=ResponseContext(
                name=context_result.name,
                app_name=context_result.app_name,
                display_name=context_result.display_name,
                namespace_name=context_result.namespace_name,
                resource_url=f"{COMPLETE_URL}/contexts/{context_result.app_name}/{context_result.namespace_name}/{context_result.name}",
            )
        )

    async def to_context_edit(
        self,
        api_request: ContextEditRequest,
    ) -> Tuple[ContextGetQuery, Dict[str, Any]]:
        query = ContextGetQuery(
            name=api_request.name,
            namespace_name=api_request.namespace_name,
            app_name=api_request.app_name,
        )
        changed_data = api_request.data.model_dump(exclude_unset=True)
        return query, changed_data

    async def to_contexts_get(
        self, api_request: Union[GetAllRequest, GetByAppRequest, GetByNamespaceRequest]
    ) -> ContextsGetQuery:
        return ContextsGetQuery(
            pagination=PaginationRequest(
                query_offset=api_request.offset,
                query_limit=api_request.limit,
            ),
            app_name=getattr(api_request, "app_name", None),
            namespace_name=getattr(api_request, "namespace_name", None),
        )

    async def to_context_create(self, api_request: ContextCreateRequest) -> Context:
        return Context(
            name=api_request.data.name,
            display_name=api_request.data.display_name,
            app_name=api_request.app_name,
            namespace_name=api_request.namespace_name,
        )

    async def to_api_create_response(
        self, context_result: Context
    ) -> ContextSingleResponse:
        return ContextSingleResponse(
            context=ResponseContext(
                name=context_result.name,
                app_name=context_result.app_name,
                display_name=context_result.display_name,
                namespace_name=context_result.namespace_name,
                resource_url=f"{COMPLETE_URL}/contexts/{context_result.app_name}/{context_result.namespace_name}/{context_result.name}",
            )
        )

    async def to_api_get_response(
        self, context_result: Context
    ) -> ContextSingleResponse:
        return ContextSingleResponse(
            context=ResponseContext(
                name=context_result.name,
                app_name=context_result.app_name,
                display_name=context_result.display_name,
                namespace_name=context_result.namespace_name,
                resource_url=f"{COMPLETE_URL}/contexts/{context_result.app_name}/{context_result.namespace_name}/{context_result.name}",
            )
        )

    async def to_context_get(self, api_request: ContextGetRequest) -> ContextGetQuery:
        return ContextGetQuery(
            name=api_request.name,
            app_name=api_request.app_name,
            namespace_name=api_request.namespace_name,
        )

    async def to_api_contexts_get_response(
        self,
        contexts: List[Context],
        query_offset: int,
        query_limit: Optional[int],
        total_count: int,
    ) -> ContextMultipleResponse:
        return ContextMultipleResponse(
            pagination=PaginationInfo(
                offset=query_offset,
                limit=query_limit if query_limit else total_count,  # todo?
                total_count=total_count,
            ),
            contexts=[
                ResponseContext(
                    name=context.name,
                    display_name=context.display_name,
                    app_name=context.app_name,
                    namespace_name=context.namespace_name,
                    resource_url=f"{COMPLETE_URL}/contexts/{context.app_name}/{context.namespace_name}/{context.name}",
                )
                for context in contexts
            ],
        )


class SQLContextPersistenceAdapter(
    AsyncConfiguredAdapterMixin, ContextPersistencePort, SQLAlchemyMixin
):
    @staticmethod
    def _context_to_db_context(context: Context, namespace_id: int) -> DBContext:
        return DBContext(
            namespace_id=namespace_id,
            name=context.name,
            display_name=context.display_name,
        )

    @staticmethod
    def _db_context_to_context(db_context: DBContext) -> Context:
        return Context(
            app_name=db_context.namespace.app.name,
            namespace_name=db_context.namespace.name,
            name=db_context.name,
            display_name=db_context.display_name,
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

    async def create(self, context: Context) -> Context:
        db_app = await self._get_single_object(DBApp, name=context.app_name)
        if db_app is None:
            raise ParentNotFoundError(
                "The app of the object to be created does not exist."
            )
        db_namespace = await self._get_single_object(
            DBNamespace,
            app_name=db_app.name,
            name=context.namespace_name,
        )
        if db_namespace is None:
            raise ParentNotFoundError(
                "The namespace of the object to be created does not exist."
            )
        async with self.session() as session:
            db_context = SQLContextPersistenceAdapter._context_to_db_context(
                context, db_namespace.id
            )
            result = await self._create_object(db_context, session=session)
        return SQLContextPersistenceAdapter._db_context_to_context(result)

    async def read_one(self, query: ContextGetQuery) -> Context:
        result = await self._get_single_object(
            DBContext,
            name=query.name,
            app_name=query.app_name,
            namespace_name=query.namespace_name,
        )
        if result is None:
            raise ObjectNotFoundError(
                f"No context with the identifier '{query.app_name}:"
                f"{query.namespace_name}:{query.name}' could be found."
            )
        return SQLContextPersistenceAdapter._db_context_to_context(result)

    async def read_many(
        self,
        query: ContextsGetQuery,
    ) -> PersistenceGetManyResult[Context]:
        dp_contexts, total_count = await self._get_many_objects(
            DBContext,
            query.pagination.query_offset,
            query.pagination.query_limit,
            app_name=query.app_name,
            namespace_name=query.namespace_name,
        )
        contexts = [
            SQLContextPersistenceAdapter._db_context_to_context(db_context)
            for db_context in dp_contexts
        ]
        return PersistenceGetManyResult(total_count=total_count, objects=contexts)

    async def update(self, context: Context) -> Context:
        db_context = await self._get_single_object(
            DBContext,
            name=context.name,
            app_name=context.app_name,
            namespace_name=context.namespace_name,
        )
        if db_context is None:
            raise ObjectNotFoundError(
                f"No context with the identifier '{context.app_name}:"
                f"{context.namespace_name}:{context.name}' could be found."
            )
        modified = await self._update_object(
            db_context, display_name=context.display_name
        )
        return SQLContextPersistenceAdapter._db_context_to_context(modified)
