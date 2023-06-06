"""
Proposed layout for permission ports/models
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
    def create(
        self,
        app_name: str,
        namespace_name: str,
        permission_name: str,
        display_name: Optional[str] = None,
    ) -> PermissionAPIResponse:
        pass

    def read_one(
        self,
        app_name: str,
        namespace_name: str,
        permission_name: str,
    ) -> PermissionAPIResponse:
        pass

    def read_many(
        self,
        app_name: Optional[str] = None,
        namespace_name: Optional[str] = None,
        pagination_offset: Optional[int] = None,
        pagination_limit: Optional[int] = None,
    ) -> PermissionsListAPIResponse:
        pass

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
    async def create(
        self,
        permission: Permission,
    ) -> Permission:
        pass

    async def read_one(
        self,
        app_name: str,
        namespace_name: str,
        permission_name: str,
    ) -> Permission:
        pass

    async def read_many(
        self,
        app_name: Optional[str] = None,
        namespace_name: Optional[str] = None,
        query_offset: Optional[int] = None,
        query_limit: Optional[int] = None,
    ) -> PermissionQuery:
        pass

    async def update(
        self,
        permission: Permission,
    ) -> Permission:
        pass
