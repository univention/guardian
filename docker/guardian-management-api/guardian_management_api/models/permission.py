# Copyright (C) 2023 Univention GmbH
#
# SPDX-License-Identifier: AGPL-3.0-only
"""
Permission-related models
"""

from dataclasses import dataclass
from typing import List, Optional

from .base import (
    NamespacedObject,
    PaginatedAPIResponse,
    PaginationRequest,
    QueryResponse,
    ResponseObject,
)


@dataclass(frozen=True)
class Permission(NamespacedObject):
    display_name: Optional[str] = None


class PermissionQueryResponse(QueryResponse):
    permissions: List[Permission]


@dataclass(frozen=True)
class PermissionCreateQuery:
    permissions: List[Permission]


@dataclass(frozen=True)
class PermissionGetQuery(NamespacedObject):
    ...


@dataclass(frozen=True)
class PermissionEditQuery:
    permission: Permission


@dataclass(frozen=True)
class PermissionsGetQuery:
    pagination: PaginationRequest
    app_name: Optional[str] = None
    namespace_name: Optional[str] = None


@dataclass(frozen=True)
class ResponsePermission(ResponseObject):
    name: str
    display_name: Optional[str]


@dataclass(frozen=True)
class PermissionAPIResponse:
    permission: ResponsePermission


@dataclass(frozen=True)
class PermissionListAPIResponse(PaginatedAPIResponse):
    permissions: List[ResponsePermission]
