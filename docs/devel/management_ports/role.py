# Copyright (C) 2023 Univention GmbH
#
# SPDX-License-Identifier: AGPL-3.0-only

"""
Proposed layout for role ports/models
"""

from dataclasses import dataclass
from typing import List, Optional

from .base import (
    BasePort,
    NamespacedPersistenceObject,
    NamespacedResponseObject,
    PaginatedAPIResponse,
    QueryResponse,
)

###############################################################################
#                                                                             #
#  Models                                                                     #
#                                                                             #
###############################################################################


class Role(NamespacedPersistenceObject):
    ...


class RoleQuery(QueryResponse):
    roles: List[Role]


class ResponseRole(NamespacedResponseObject):
    ...


@dataclass
class RoleAPIResponse:
    role: ResponseRole


class RolesListAPIResponse(PaginatedAPIResponse):
    roles: List[ResponseRole]


###############################################################################
#                                                                             #
#  Incoming ports                                                             #
#                                                                             #
###############################################################################


class RoleAPIPort(BasePort):
    def create(
        self,
        app_name: str,
        namespace_name: str,
        role_name: str,
        display_name: Optional[str] = None,
    ) -> RoleAPIResponse:
        pass

    def read_one(
        self,
        app_name: str,
        namespace_name: str,
        role_name: str,
    ) -> RoleAPIResponse:
        pass

    def read_many(
        self,
        app_name: Optional[str] = None,
        namespace_name: Optional[str] = None,
        pagination_offset: Optional[int] = None,
        pagination_limit: Optional[int] = None,
    ) -> RolesListAPIResponse:
        pass

    def update(
        self,
        app_name: str,
        namespace_name: str,
        role_name: str,
        display_name: str,
    ) -> RoleAPIResponse:
        pass


###############################################################################
#                                                                             #
#  Outgoing ports                                                             #
#                                                                             #
###############################################################################


class RolePersistencePort(BasePort):
    async def create(
        self,
        role: Role,
    ) -> Role:
        pass

    async def read_one(
        self,
        app_name: str,
        namespace_name: str,
        role_name: str,
    ) -> Role:
        pass

    async def read_many(
        self,
        app_name: Optional[str] = None,
        namespace_name: Optional[str] = None,
        query_offset: Optional[int] = None,
        query_limit: Optional[int] = None,
    ) -> RoleQuery:
        pass

    async def update(
        self,
        role: Role,
    ) -> Role:
        pass
