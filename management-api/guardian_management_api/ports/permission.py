# Copyright (C) 2023 Univention GmbH
#
# SPDX-License-Identifier: AGPL-3.0-only

"""
Proposed layout for permission ports/models
"""

from abc import abstractmethod
from dataclasses import dataclass
from typing import List, Optional

from ..models.base import (
    NamespacedPersistenceObject,
    NamespacedResponseObject,
    PaginatedAPIResponse,
    QueryResponse,
)
from .base import (
    BasePort,
)

###############################################################################
#                                                                             #
#  Models                                                                     #
#                                                                             #
###############################################################################


class Permission(NamespacedPersistenceObject):
    ...


class PermissionQuery(QueryResponse):
    permissions: List[Permission]


class ResponsePermission(NamespacedResponseObject):
    ...


@dataclass
class PermissionAPIResponse:
    permission: ResponsePermission


class PermissionsListAPIResponse(PaginatedAPIResponse):
    permissions: List[ResponsePermission]


###############################################################################
#                                                                             #
#  Incoming ports                                                             #
#                                                                             #
###############################################################################


class PermissionAPIPort(BasePort):
    @abstractmethod
    def create(
        self,
        app_name: str,
        namespace_name: str,
        permission_name: str,
        display_name: Optional[str] = None,
    ) -> PermissionAPIResponse:
        pass

    @abstractmethod
    def read_one(
        self,
        app_name: str,
        namespace_name: str,
        permission_name: str,
    ) -> PermissionAPIResponse:
        pass

    @abstractmethod
    def read_many(
        self,
        app_name: Optional[str] = None,
        namespace_name: Optional[str] = None,
        pagination_offset: Optional[int] = None,
        pagination_limit: Optional[int] = None,
    ) -> PermissionsListAPIResponse:
        pass

    @abstractmethod
    def update(
        self,
        app_name: str,
        namespace_name: str,
        permission_name: str,
        display_name: str,
    ) -> PermissionAPIResponse:
        pass


###############################################################################
#                                                                             #
#  Outgoing ports                                                             #
#                                                                             #
###############################################################################


class PermissionPersistencePort(BasePort):
    @abstractmethod
    async def create(
        self,
        permission: Permission,
    ) -> Permission:
        pass

    @abstractmethod
    async def read_one(
        self,
        app_name: str,
        namespace_name: str,
        permission_name: str,
    ) -> Permission:
        pass

    @abstractmethod
    async def read_many(
        self,
        app_name: Optional[str] = None,
        namespace_name: Optional[str] = None,
        query_offset: Optional[int] = None,
        query_limit: Optional[int] = None,
    ) -> PermissionQuery:
        pass

    @abstractmethod
    async def update(
        self,
        permission: Permission,
    ) -> Permission:
        pass
