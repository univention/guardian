# Copyright (C) 2023 Univention GmbH
#
# SPDX-License-Identifier: AGPL-3.0-only

"""
Proposed layout for role ports/models
"""

from abc import ABC, abstractmethod
from typing import Generic, List, Optional, TypeVar

from guardian_lib.ports import BasePort

from ..models.role import (
    Role,
    RoleCreateQuery,
    RoleGetQuery,
    RolesGetQuery,
)
from .base import BasePersistencePort

RoleAPICreateRequestObject = TypeVar("RoleAPICreateRequestObject")
RoleAPICreateResponseObject = TypeVar("RoleAPICreateResponseObject")

RoleAPIGetRequestObject = TypeVar("RoleAPIGetRequestObject")
RoleAPIGetResponseObject = TypeVar("RoleAPIGetResponseObject")

RoleAPIGetMultipleRequestObject = TypeVar("RoleAPIGetMultipleRequestObject")
RoleAPIGetMultipleResponseObject = TypeVar("RoleAPIGetMultipleResponseObject")


###############################################################################
#                                                                             #
#  Incoming ports                                                             #
#                                                                             #
###############################################################################


class RoleAPIPort(
    BasePort,
    ABC,
    Generic[
        RoleAPICreateRequestObject,
        RoleAPICreateResponseObject,
        RoleAPIGetRequestObject,
        RoleAPIGetResponseObject,
        RoleAPIGetMultipleRequestObject,
        RoleAPIGetMultipleResponseObject,
    ],
):
    @abstractmethod
    async def transform_exception(self, exc: Exception) -> Exception:
        raise NotImplementedError  # pragma: no cover

    @abstractmethod
    async def to_role_create(
        self, api_request: RoleAPICreateRequestObject
    ) -> RoleCreateQuery:
        raise NotImplementedError  # pragma: no cover

    @abstractmethod
    async def to_role_create_response(
        self, role_result: Role
    ) -> RoleAPICreateResponseObject:
        raise NotImplementedError  # pragma: no cover

    @abstractmethod
    async def to_role_get(self, api_request: RoleAPIGetRequestObject) -> RoleGetQuery:
        raise NotImplementedError  # pragma: no cover

    @abstractmethod
    async def to_role_get_response(self, role_result: Role) -> RoleAPIGetResponseObject:
        raise NotImplementedError  # pragma: no cover

    @abstractmethod
    async def to_roles_get(
        self, api_request: RoleAPIGetMultipleRequestObject
    ) -> RolesGetQuery:
        raise NotImplementedError  # pragma: no cover

    @abstractmethod
    async def to_roles_get_response(
        self,
        roles: List[Role],
        query_offset: int,
        query_limit: Optional[int],
        total_count: int,
    ) -> RoleAPIGetMultipleResponseObject:
        raise NotImplementedError  # pragma: no cover

    @abstractmethod
    async def to_role_edit(self, old_role: Role, display_name: Optional[str]) -> Role:
        raise NotImplementedError  # pragma: no cover


###############################################################################
#                                                                             #
#  Outgoing ports                                                             #
#                                                                             #
###############################################################################


class RolePersistencePort(
    BasePersistencePort[Role, RoleGetQuery, RolesGetQuery], ABC
): ...
