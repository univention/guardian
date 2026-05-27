# Copyright (C) 2023 Univention GmbH
#
# SPDX-License-Identifier: AGPL-3.0-only

from dataclasses import dataclass, field
from typing import List, Optional

from .base import PaginatedAPIResponse, PaginationRequest, ResponseObject
from .flags import Flag
from .capability import Capability


@dataclass
class Role:
    app_name: str
    namespace_name: str
    name: str
    display_name: Optional[str] = None
    flags: Flag = Flag.NONE
    capabilities: list[Capability] = field(default_factory=list)


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
