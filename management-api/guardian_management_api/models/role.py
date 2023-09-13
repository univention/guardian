# Copyright (C) 2023 Univention GmbH
#
# SPDX-License-Identifier: AGPL-3.0-only

from dataclasses import dataclass
from typing import List, Optional

from .base import PaginatedAPIResponse, PaginationRequest, ResponseObject


@dataclass(frozen=True)
class Role:
    app_name: str
    namespace_name: str
    name: str
    display_name: Optional[str] = None


@dataclass(frozen=True)
class RoleCreateQuery:
    roles: List[Role]


@dataclass(frozen=True)
class RoleGetQuery:
    app_name: str
    namespace_name: str
    name: str


@dataclass(frozen=True)
class RolesGetQuery:
    pagination: PaginationRequest
    app_name: Optional[str] = None
    namespace_name: Optional[str] = None


@dataclass(frozen=True)
class ResponseRole(ResponseObject):
    app_name: str
    namespace_name: str
    name: str
    display_name: Optional[str]


@dataclass(frozen=True)
class RoleAPIResponse:
    role: ResponseRole


@dataclass(frozen=True)
class RolesListAPIResponse(PaginatedAPIResponse):
    roles: List[ResponseRole]
