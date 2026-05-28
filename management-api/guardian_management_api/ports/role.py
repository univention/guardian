# Copyright (C) 2023 Univention GmbH
#
# SPDX-License-Identifier: AGPL-3.0-only

"""
Proposed layout for role ports/models
"""

from abc import ABC, abstractmethod
from typing import Generic, List, Optional, TypeVar

from guardian_lib.ports import BasePort

from ..models.capability import CapabilityReference
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
    async def to_role_edit(
        self,
        old_role: Role,
        display_name: Optional[str] = None,
        capabilities: Optional[List[CapabilityReference]] = None,
    ) -> Role:
        raise NotImplementedError  # pragma: no cover


###############################################################################
#                                                                             #
#  Outgoing ports                                                             #
#                                                                             #
###############################################################################


class RolePersistencePort(BasePersistencePort[Role, RoleGetQuery, RolesGetQuery], ABC):
    async def delete(self, query: RoleGetQuery) -> None:
        """
        Deletes the specified role from the persistent storage.

        :raises ObjectNotFoundError: If the role could not be found.
        :raises PersistenceError: For any other error during interaction with the persistence.
        """
        raise NotImplementedError  # pragma: no cover

    async def read_dependencies(self, query: RoleGetQuery) -> list[CapabilityReference]:
        """
        Returns the list of capability references that reference the specified role.

        :raises PersistenceError: For any error during interaction with the persistence.
        """
        raise NotImplementedError  # pragma: no cover
