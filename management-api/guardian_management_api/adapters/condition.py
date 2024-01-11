# Copyright (C) 2023 Univention GmbH
#
# SPDX-License-Identifier: AGPL-3.0-only

from dataclasses import asdict
from typing import Any, Optional, Tuple, Type, Union

from port_loader import AsyncConfiguredAdapterMixin

from ..constants import COMPLETE_URL
from ..errors import (
    ObjectNotFoundError,
    ParentNotFoundError,
)
from ..models.base import PaginationRequest, PersistenceGetManyResult
from ..models.condition import (
    Condition,
    ConditionGetQuery,
    ConditionParameter,
    ConditionsGetQuery,
)
from ..models.routers.base import (
    GetAllRequest,
    GetByAppRequest,
    GetByNamespaceRequest,
    GetFullIdentifierRequest,
    ManagementObjectName,
    PaginationInfo,
)
from ..models.routers.condition import (
    Condition as ResponseCondition,
)
from ..models.routers.condition import (
    ConditionCreateRequest,
    ConditionEditRequest,
    ConditionMultipleResponse,
    ConditionParameterName,
    ConditionSingleResponse,
)
from ..models.routers.condition import (
    ConditionParameter as ResponseConditionParameter,
)
from ..models.sql_persistence import (
    DBApp,
    DBCondition,
    DBConditionParameter,
    DBNamespace,
    SQLPersistenceAdapterSettings,
)
from ..ports.condition import (
    ConditionAPIPort,
    ConditionPersistencePort,
)
from .fastapi_utils import TransformExceptionMixin
from .sql_persistence import SQLAlchemyMixin


class TransformConditionExceptionMixin(TransformExceptionMixin):
    ...


class FastAPIConditionAPIAdapter(
    TransformConditionExceptionMixin,
    ConditionAPIPort[
        GetFullIdentifierRequest,
        ConditionSingleResponse,
        Union[GetAllRequest, GetByAppRequest, GetByNamespaceRequest],
        ConditionMultipleResponse,
        ConditionCreateRequest,
        ConditionEditRequest,
    ],
):
    class Config:
        alias = "fastapi"

    async def to_obj_get_single(
        self, api_request: GetFullIdentifierRequest
    ) -> ConditionGetQuery:
        return ConditionGetQuery(
            app_name=api_request.app_name,
            namespace_name=api_request.namespace_name,
            name=api_request.name,
        )

    async def to_api_get_single_response(
        self, obj: Condition
    ) -> ConditionSingleResponse:
        return ConditionSingleResponse(
            condition=ResponseCondition(
                app_name=ManagementObjectName(obj.app_name),
                namespace_name=ManagementObjectName(obj.namespace_name),
                name=ManagementObjectName(obj.name),
                display_name=obj.display_name,
                parameters=[
                    ResponseConditionParameter(
                        name=ConditionParameterName(cond_param.name),
                        value_type=cond_param.value_type,
                    )
                    for cond_param in obj.parameters
                ],
                documentation=obj.documentation,
                resource_url=f"{COMPLETE_URL}/conditions/{obj.app_name}/{obj.namespace_name}/{obj.name}",
            )
        )

    async def to_obj_get_multiple(
        self, api_request: Union[GetAllRequest, GetByAppRequest, GetByNamespaceRequest]
    ) -> ConditionsGetQuery:
        return ConditionsGetQuery(
            pagination=PaginationRequest(
                query_offset=api_request.offset, query_limit=api_request.limit
            ),
            app_name=getattr(api_request, "app_name", None),
            namespace_name=getattr(api_request, "namespace_name", None),
        )

    async def to_api_get_multiple_response(
        self,
        objs: list[Condition],
        query_offset: int,
        query_limit: Optional[int],
        total_count: int,
    ) -> ConditionMultipleResponse:
        return ConditionMultipleResponse(
            conditions=[
                ResponseCondition(
                    app_name=ManagementObjectName(condition.app_name),
                    namespace_name=ManagementObjectName(condition.namespace_name),
                    name=ManagementObjectName(condition.name),
                    display_name=condition.display_name,
                    documentation=condition.documentation,
                    parameters=[
                        ResponseConditionParameter(
                            name=ConditionParameterName(cond_param.name),
                            value_type=cond_param.value_type,
                        )
                        for cond_param in condition.parameters
                    ],
                    resource_url=f"{COMPLETE_URL}/conditions/{condition.app_name}/{condition.namespace_name}/{condition.name}",
                )
                for condition in objs
            ],
            pagination=PaginationInfo(
                offset=query_offset,
                limit=query_limit if query_limit else total_count,
                total_count=total_count,
            ),
        )

    async def to_obj_create(self, api_request: ConditionCreateRequest) -> Condition:
        return Condition(
            app_name=api_request.app_name,
            namespace_name=api_request.namespace_name,
            name=api_request.data.name,
            display_name=api_request.data.display_name,
            documentation=api_request.data.documentation,
            code=api_request.data.code if api_request.data.code else b"",
            parameters=[
                ConditionParameter(
                    name=cond_param.name, value_type=cond_param.value_type
                )
                for cond_param in api_request.data.parameters
            ],
        )

    async def to_obj_edit(
        self, api_request: ConditionEditRequest
    ) -> Tuple[ConditionGetQuery, dict[str, Any]]:
        query = ConditionGetQuery(
            app_name=api_request.app_name,
            namespace_name=api_request.namespace_name,
            name=api_request.name,
        )
        changed_data = api_request.data.dict(exclude_unset=True)
        return query, changed_data


class SQLConditionPersistenceAdapter(
    AsyncConfiguredAdapterMixin, ConditionPersistencePort, SQLAlchemyMixin
):
    @staticmethod
    def _condition_to_db_condition(
        condition: Condition, namespace_id: int
    ) -> DBCondition:
        return DBCondition(
            namespace_id=namespace_id,
            name=condition.name,
            display_name=condition.display_name,
            documentation=condition.documentation,
            parameters=[
                DBConditionParameter(
                    name=cond_param.name, value_type=cond_param.value_type, position=idx
                )
                for idx, cond_param in enumerate(condition.parameters)
            ],
            code=condition.code,
        )

    @staticmethod
    def _db_condition_to_condition(db_condition: DBCondition) -> Condition:
        return Condition(
            app_name=db_condition.namespace.app.name,
            namespace_name=db_condition.namespace.name,
            name=db_condition.name,
            display_name=db_condition.display_name,
            documentation=db_condition.documentation,
            parameters=[
                ConditionParameter(
                    name=cond_param.name, value_type=cond_param.value_type
                )
                for cond_param in db_condition.parameters
            ],
            code=db_condition.code,
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

    async def create(self, condition: Condition) -> Condition:
        db_app = await self._get_single_object(DBApp, name=condition.app_name)
        if db_app is None:
            raise ParentNotFoundError(
                "The app of the object to be created does not exist."
            )
        db_namespace = await self._get_single_object(
            DBNamespace,
            app_name=db_app.name,
            name=condition.namespace_name,
        )
        if db_namespace is None:
            raise ParentNotFoundError(
                "The namespace of the object to be created does not exist."
            )
        async with self.session() as session:
            db_condition = SQLConditionPersistenceAdapter._condition_to_db_condition(
                condition, db_namespace.id
            )
            result = await self._create_object(db_condition, session=session)
        return SQLConditionPersistenceAdapter._db_condition_to_condition(result)

    async def read_one(self, query: ConditionGetQuery) -> Condition:
        result = await self._get_single_object(
            DBCondition,
            name=query.name,
            app_name=query.app_name,
            namespace_name=query.namespace_name,
        )
        if result is None:
            raise ObjectNotFoundError(
                f"No permission with the identifier '{query.app_name}:"
                f"{query.namespace_name}:{query.name}' could be found."
            )
        return SQLConditionPersistenceAdapter._db_condition_to_condition(result)

    async def read_many(
        self,
        query: ConditionsGetQuery,
    ) -> PersistenceGetManyResult[Condition]:
        dp_conditions, total_count = await self._get_many_objects(
            DBCondition,
            query.pagination.query_offset,
            query.pagination.query_limit,
            app_name=query.app_name,
            namespace_name=query.namespace_name,
        )
        conditions = [
            SQLConditionPersistenceAdapter._db_condition_to_condition(db_condition)
            for db_condition in dp_conditions
        ]
        return PersistenceGetManyResult(total_count=total_count, objects=conditions)

    async def update(self, condition: Condition) -> Condition:
        db_condition = await self._get_single_object(
            DBCondition,
            name=condition.name,
            app_name=condition.app_name,
            namespace_name=condition.namespace_name,
        )
        if db_condition is None:
            raise ObjectNotFoundError(
                f"No condition with the identifier '{condition.app_name}:"
                f"{condition.namespace_name}:{condition.name}' could be found."
            )
        modified = await self._update_object(
            db_condition,
            display_name=condition.display_name,
            documentation=condition.documentation,
            parameters=[
                DBConditionParameter(
                    name=cond_param.name, value_type=cond_param.value_type, position=idx
                )
                for idx, cond_param in enumerate(condition.parameters)
            ],
            code=condition.code,
        )
        return SQLConditionPersistenceAdapter._db_condition_to_condition(modified)
