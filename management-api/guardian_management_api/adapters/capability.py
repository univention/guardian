# Copyright (C) 2023 Univention GmbH
#
# SPDX-License-Identifier: AGPL-3.0-only
import uuid
from dataclasses import asdict
from typing import Optional, Tuple, Type, Union

from port_loader import AsyncConfiguredAdapterMixin
from sqlalchemy import select, tuple_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql.functions import count

from guardian_management_api.adapters.sql_persistence import (
    SQLAlchemyMixin,
    error_guard,
)
from guardian_management_api.constants import COMPLETE_URL
from guardian_management_api.errors import (
    ObjectNotFoundError,
    ParentNotFoundError,
)
from guardian_management_api.models.base import (
    PaginationRequest,
    PersistenceGetManyResult,
)
from guardian_management_api.models.capability import (
    CapabilitiesByRoleQuery,
    CapabilitiesGetQuery,
    Capability,
    CapabilityConditionParameter,
    CapabilityConditionRelation,
    CapabilityGetQuery,
    ParametrizedCondition,
)
from guardian_management_api.models.condition import Condition
from guardian_management_api.models.permission import Permission
from guardian_management_api.models.role import Role
from guardian_management_api.models.routers.base import (
    GetAllRequest,
    GetByNamespaceRequest,
    GetFullIdentifierRequest,
    ManagementObjectName,
    PaginationInfo,
)
from guardian_management_api.models.routers.capability import (
    CapabilitiesGetByRoleRequest,
    CapabilityCondition,
    CapabilityCreateRequest,
    CapabilityEditRequest,
    CapabilityMultipleResponse,
    CapabilityPermission,
    CapabilityRole,
    CapabilitySingleResponse,
    RelationChoices,
)
from guardian_management_api.models.routers.capability import (
    Capability as ResponseCapability,
)
from guardian_management_api.models.routers.capability import (
    CapabilityConditionParameter as ResponseCapCondParam,
)
from guardian_management_api.models.routers.condition import ConditionParameterName
from guardian_management_api.models.sql_persistence import (
    DBApp,
    DBCapability,
    DBCapabilityCondition,
    DBCondition,
    DBNamespace,
    DBPermission,
    DBRole,
    SQLPersistenceAdapterSettings,
)
from guardian_management_api.ports.capability import (
    CapabilityAPIPort,
    CapabilityPersistencePort,
)

from .fastapi_utils import TransformExceptionMixin


class TransformCapabilityExceptionMixin(TransformExceptionMixin): ...


class SQLCapabilityPersistenceAdapter(
    AsyncConfiguredAdapterMixin, CapabilityPersistencePort, SQLAlchemyMixin
):
    class Config:
        alias = "sql"
        cached = True

    @staticmethod
    def _cap_to_db_cap(
        cap: Capability,
        namespace_id: int,
        role_id: int,
        db_permissions: list[DBPermission],
        db_conditions: list[DBCondition],
    ) -> DBCapability:
        db_conditions_dict = {
            f"{db_cond.namespace.app.name}:{db_cond.namespace.name}:{db_cond.name}": db_cond
            for db_cond in db_conditions
        }
        cap_conditions = set()
        for cond in cap.conditions:
            db_cond = db_conditions_dict[
                f"{cond.app_name}:{cond.namespace_name}:{cond.name}"
            ]
            db_cond_params_dict = {param.name: param for param in db_cond.parameters}
            cap_conditions.add(
                DBCapabilityCondition(
                    condition_id=db_cond.id,
                    kwargs=[
                        {
                            "name": param.name,
                            "value": param.value,
                            "value_type": db_cond_params_dict[param.name].value_type,
                        }
                        for param in cond.parameters
                    ],
                )
            )
        return DBCapability(
            namespace_id=namespace_id,
            name=cap.name,
            display_name=cap.display_name,
            role_id=role_id,
            relation=cap.relation,
            permissions=set(db_permissions),
            conditions=cap_conditions,
        )

    @staticmethod
    def _db_cap_to_cap(db_cap: DBCapability) -> Capability:
        conditions = []
        for cap_cond in db_cap.conditions:
            db_cond_parameters = {
                param.name: param for param in cap_cond.condition.parameters
            }
            conditions.append(
                ParametrizedCondition(
                    app_name=cap_cond.condition.namespace.app.name,
                    namespace_name=cap_cond.condition.namespace.name,
                    name=cap_cond.condition.name,
                    parameters=[
                        CapabilityConditionParameter(
                            name=param["name"],
                            value=param["value"],
                            value_type=db_cond_parameters[param["name"]].value_type,
                        )
                        for param in cap_cond.kwargs
                    ],
                )
            )
        return Capability(
            app_name=db_cap.namespace.app.name,
            namespace_name=db_cap.namespace.name,
            name=db_cap.name,
            display_name=db_cap.display_name,
            role=Role(
                app_name=db_cap.role.namespace.app.name,
                namespace_name=db_cap.role.namespace.name,
                name=db_cap.role.name,
            ),
            permissions=[
                Permission(
                    app_name=perm.namespace.app.name,
                    namespace_name=perm.namespace.name,
                    name=perm.name,
                )
                for perm in db_cap.permissions
            ],
            relation=db_cap.relation,
            conditions=conditions,
        )

    @classmethod
    def get_settings_cls(
        cls,
    ) -> Type[SQLPersistenceAdapterSettings]:  # pragma: no cover
        return SQLPersistenceAdapterSettings

    async def configure(self, settings: SQLPersistenceAdapterSettings):
        self._db_string = SQLAlchemyMixin.create_db_string(**asdict(settings))

    @SQLAlchemyMixin.session_wrapper
    async def _get_db_child_objs_for_capability(
        self,
        obj_type: Type[DBPermission | DBCondition],
        objs: list[Permission | ParametrizedCondition],
        *,
        session: AsyncSession,
    ) -> list[DBPermission | DBCondition]:
        objs_identifiers = [
            (obj.app_name, obj.namespace_name, obj.name) for obj in objs
        ]
        stmt = (
            select(obj_type)
            .order_by(DBApp.name, DBNamespace.name, obj_type.name)
            .join(DBNamespace, obj_type.namespace_id == DBNamespace.id)  # type: ignore[arg-type]
            .join(DBApp, DBNamespace.app_id == DBApp.id)  # type: ignore[arg-type]
            .where(
                tuple_(DBApp.name, DBNamespace.name, obj_type.name).in_(  # type: ignore[arg-type]
                    objs_identifiers
                )
            )
        )
        result = list((await session.scalars(stmt)).unique().all())
        if len(result) != len(set(objs_identifiers)):
            raise ObjectNotFoundError(
                f"Not all {'permissions' if obj_type is DBPermission else 'conditions'} "
                f"specified for the capability could be found.",
                object_type=Permission if obj_type is DBPermission else Condition,
            )
        return result  # type: ignore[return-value]

    async def create(self, obj: Capability) -> Capability:
        db_namespace = await self._get_single_object(
            DBNamespace, app_name=obj.app_name, name=obj.namespace_name
        )
        if db_namespace is None:
            raise ParentNotFoundError(
                "The namespace of the capability to create does not exist."
            )
        db_role = await self._get_single_object(
            DBRole,
            app_name=obj.role.app_name,
            namespace_name=obj.role.namespace_name,
            name=obj.role.name,
        )
        if db_role is None:
            raise ObjectNotFoundError(
                "The capabilities role could not be found.", object_type=Role
            )
        async with self.session() as session:
            permissions: list[DBPermission] = (
                await self._get_db_child_objs_for_capability(
                    DBPermission, obj.permissions, session=session
                )
            )
            conditions: list[DBCondition] = (
                await self._get_db_child_objs_for_capability(
                    DBCondition, obj.conditions, session=session
                )
            )
        db_cap = SQLCapabilityPersistenceAdapter._cap_to_db_cap(
            obj, db_namespace.id, db_role.id, permissions, conditions
        )
        result = await self._create_object(db_cap)
        return SQLCapabilityPersistenceAdapter._db_cap_to_cap(result)

    async def update(self, obj: Capability) -> Capability:
        # This can probably be implemented without deleting objects, but since there
        # is currently no disadvantage, this is the easiest way to implement this.
        await self.delete(
            CapabilityGetQuery(
                app_name=obj.app_name, namespace_name=obj.namespace_name, name=obj.name
            )
        )
        return await self.create(obj)

    async def delete(self, query: CapabilityGetQuery) -> None:
        db_capability = await self._get_single_object(
            DBCapability,
            name=query.name,
            app_name=query.app_name,
            namespace_name=query.namespace_name,
        )
        if db_capability is None:
            raise ObjectNotFoundError(
                f"No capability with the identifier '{query.app_name}:"
                f"{query.namespace_name}:{query.name}' could be found.",
                object_type=Capability,
            )
        await self._delete_obj(db_capability)

    async def read_one(self, query: CapabilityGetQuery) -> Capability:
        result = await self._get_single_object(
            DBCapability,
            name=query.name,
            app_name=query.app_name,
            namespace_name=query.namespace_name,
        )
        if result is None:
            raise ObjectNotFoundError(
                f"No capability with the identifier '{query.app_name}:"
                f"{query.namespace_name}:{query.name}' could be found.",
                object_type=Capability,
            )
        return SQLCapabilityPersistenceAdapter._db_cap_to_cap(result)

    @staticmethod
    def _configure_search_stmt_by_role(
        stmt, app_name: str, namespace_name: str, name: str
    ):
        return (
            stmt.join(DBRole, DBCapability.role_id == DBRole.id)
            .join(DBNamespace, DBRole.namespace_id == DBNamespace.id)
            .join(DBApp, DBNamespace.app_id == DBApp.id)
            .where(
                DBApp.name == app_name,
                DBNamespace.name == namespace_name,
                DBRole.name == name,
            )
        )

    @error_guard
    @SQLAlchemyMixin.session_wrapper
    async def _get_capabilities_by_role(
        self, query: CapabilitiesByRoleQuery, *, session: AsyncSession
    ) -> Tuple[list[DBCapability], int]:
        select_stmt = (
            select(DBCapability)
            .offset(query.pagination.query_offset)
            .order_by(DBCapability.name)
        )
        count_stmt = select(count(DBCapability.id))
        if query.pagination.query_limit:
            select_stmt = select_stmt.limit(query.pagination.query_limit)
        select_stmt = SQLCapabilityPersistenceAdapter._configure_search_stmt_by_role(
            select_stmt, query.app_name, query.namespace_name, query.role_name
        )
        count_stmt = SQLCapabilityPersistenceAdapter._configure_search_stmt_by_role(
            count_stmt, query.app_name, query.namespace_name, query.role_name
        )
        return (
            list((await session.scalars(select_stmt)).unique().all()),
            await session.scalar(count_stmt),  # type: ignore[return-value]
        )

    async def read_many(
        self, query: Union[CapabilitiesGetQuery, CapabilitiesByRoleQuery]
    ) -> PersistenceGetManyResult[Capability]:
        if isinstance(query, CapabilitiesGetQuery):
            db_conditions, total_count = await self._get_many_objects(
                DBCapability,
                query.pagination.query_offset,
                query.pagination.query_limit,
                app_name=query.app_name,
                namespace_name=query.namespace_name,
            )
        elif isinstance(query, CapabilitiesByRoleQuery):
            db_conditions, total_count = await self._get_capabilities_by_role(query)
        else:
            raise RuntimeError("Unknown query type.")
        capabilities = [
            SQLCapabilityPersistenceAdapter._db_cap_to_cap(db_cap)
            for db_cap in db_conditions
        ]
        return PersistenceGetManyResult(total_count=total_count, objects=capabilities)


class FastAPICapabilityAPIAdapter(
    TransformCapabilityExceptionMixin,
    CapabilityAPIPort[
        GetFullIdentifierRequest,
        CapabilitySingleResponse,
        Union[GetAllRequest, GetByNamespaceRequest, CapabilitiesGetByRoleRequest],
        CapabilityMultipleResponse,
        CapabilityCreateRequest,
        CapabilityEditRequest,
    ],
):
    @staticmethod
    def _cap_to_response_cap(obj: Capability):
        permissions = [
            CapabilityPermission(
                app_name=ManagementObjectName(perm.app_name),
                namespace_name=ManagementObjectName(perm.namespace_name),
                name=ManagementObjectName(perm.name),
            )
            for perm in obj.permissions
        ]
        conditions = [
            CapabilityCondition(
                app_name=ManagementObjectName(cond.app_name),
                namespace_name=ManagementObjectName(cond.namespace_name),
                name=ManagementObjectName(cond.name),
                parameters=[
                    ResponseCapCondParam(
                        name=ConditionParameterName(param.name),
                        value=param.value,
                        value_type=param.value_type,
                    )
                    for param in cond.parameters
                ],
            )
            for cond in obj.conditions
        ]
        return ResponseCapability(
            app_name=ManagementObjectName(obj.app_name),
            namespace_name=ManagementObjectName(obj.namespace_name),
            name=ManagementObjectName(obj.name),
            display_name=obj.display_name,
            relation=(
                RelationChoices.AND
                if obj.relation == CapabilityConditionRelation.AND
                else RelationChoices.OR
            ),
            role=CapabilityRole(
                app_name=ManagementObjectName(obj.role.app_name),
                namespace_name=ManagementObjectName(obj.role.namespace_name),
                name=ManagementObjectName(obj.role.name),
            ),
            resource_url=f"{COMPLETE_URL}/capabilities/{obj.app_name}/{obj.namespace_name}/{obj.name}",
            permissions=permissions,
            conditions=conditions,
        )

    async def to_obj_get_single(
        self, api_request: GetFullIdentifierRequest
    ) -> CapabilityGetQuery:
        return CapabilityGetQuery(
            app_name=api_request.app_name,
            namespace_name=api_request.namespace_name,
            name=api_request.name,
        )

    async def to_api_get_single_response(
        self, obj: Capability
    ) -> CapabilitySingleResponse:
        return CapabilitySingleResponse(
            capability=FastAPICapabilityAPIAdapter._cap_to_response_cap(obj)
        )

    async def to_obj_get_multiple(
        self,
        api_request: Union[
            GetAllRequest, GetByNamespaceRequest, CapabilitiesGetByRoleRequest
        ],
    ) -> CapabilitiesGetQuery | CapabilitiesByRoleQuery:
        if type(api_request) not in (
            GetAllRequest,
            GetByNamespaceRequest,
            CapabilitiesGetByRoleRequest,
        ):
            raise RuntimeError("Wrong request type.")
        pagination = PaginationRequest(
            query_limit=api_request.limit, query_offset=api_request.offset
        )
        if isinstance(api_request, CapabilitiesGetByRoleRequest):
            return CapabilitiesByRoleQuery(
                pagination=pagination,
                app_name=api_request.app_name,
                namespace_name=api_request.namespace_name,
                role_name=api_request.name,
            )
        elif isinstance(api_request, GetByNamespaceRequest):
            return CapabilitiesGetQuery(
                pagination=pagination,
                app_name=api_request.app_name,
                namespace_name=api_request.namespace_name,
            )
        else:
            return CapabilitiesGetQuery(pagination=pagination)

    async def to_api_get_multiple_response(
        self,
        objs: list[Capability],
        query_offset: int,
        query_limit: Optional[int],
        total_count: int,
    ) -> CapabilityMultipleResponse:
        return CapabilityMultipleResponse(
            capabilities=[
                FastAPICapabilityAPIAdapter._cap_to_response_cap(cap) for cap in objs
            ],
            pagination=PaginationInfo(
                total_count=total_count,
                offset=query_offset,
                limit=query_limit if query_limit else len(objs),
            ),
        )

    async def to_obj_create(self, api_request: CapabilityCreateRequest) -> Capability:
        return Capability(
            app_name=api_request.app_name,
            namespace_name=api_request.namespace_name,
            name=(
                api_request.data.name
                if api_request.data.name
                else f"cap-{str(uuid.uuid4())}"
            ),
            display_name=api_request.data.display_name,
            relation=(
                CapabilityConditionRelation.AND
                if api_request.data.relation == RelationChoices.AND
                else CapabilityConditionRelation.OR
            ),
            role=Role(
                app_name=api_request.data.role.app_name,
                namespace_name=api_request.data.role.namespace_name,
                name=api_request.data.role.name,
            ),
            permissions=[
                Permission(
                    app_name=perm.app_name,
                    namespace_name=perm.namespace_name,
                    name=perm.name,
                )
                for perm in api_request.data.permissions
            ],
            conditions=[
                ParametrizedCondition(
                    app_name=cond.app_name,
                    namespace_name=cond.namespace_name,
                    name=cond.name,
                    parameters=[
                        CapabilityConditionParameter(name=param.name, value=param.value)
                        for param in cond.parameters
                    ],
                )
                for cond in api_request.data.conditions
            ],
        )

    async def to_obj_edit(self, api_request: CapabilityEditRequest) -> Capability:
        return Capability(
            app_name=api_request.app_name,
            namespace_name=api_request.namespace_name,
            name=api_request.name,
            display_name=api_request.data.display_name,
            relation=(
                CapabilityConditionRelation.AND
                if api_request.data.relation == RelationChoices.AND
                else CapabilityConditionRelation.OR
            ),
            role=Role(
                app_name=api_request.data.role.app_name,
                namespace_name=api_request.data.role.namespace_name,
                name=api_request.data.role.name,
            ),
            permissions=[
                Permission(
                    app_name=perm.app_name,
                    namespace_name=perm.namespace_name,
                    name=perm.name,
                )
                for perm in api_request.data.permissions
            ],
            conditions=[
                ParametrizedCondition(
                    app_name=cond.app_name,
                    namespace_name=cond.namespace_name,
                    name=cond.name,
                    parameters=[
                        CapabilityConditionParameter(name=param.name, value=param.value)
                        for param in cond.parameters
                    ],
                )
                for cond in api_request.data.conditions
            ],
        )
