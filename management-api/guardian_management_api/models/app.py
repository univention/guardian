# Copyright (C) 2023 Univention GmbH
#
# SPDX-License-Identifier: AGPL-3.0-only

"""
App-related models
"""

from dataclasses import dataclass
from typing import List, Optional

from .base import PaginatedAPIResponse, PaginationRequest, QueryResponse, ResponseObject
from .role import ResponseRole


@dataclass
class App:
    name: str
    display_name: Optional[str] = None


@dataclass(frozen=True)
class AppQueryResponse(QueryResponse):
    apps: List[App]


@dataclass(frozen=True)
class AppCreateQuery:
    apps: List[App]


@dataclass(frozen=True)
class AppEditQuery:
    apps: List[App]


@dataclass(frozen=True)
class AppGetQuery:
    name: str


@dataclass(frozen=True)
class AppsGetQuery:
    pagination: PaginationRequest


# We're intentionally not tying this to App,
# because we'd like to make sure changes to the persistence layer doesn't
# accidentally affect the response layer.
@dataclass(frozen=True)
class ResponseApp(ResponseObject):
    name: str
    display_name: Optional[str]
    app_admin: Optional[ResponseRole]


@dataclass(frozen=True)
class AppAPIResponse:
    app: ResponseApp


@dataclass(frozen=True)
class AppsListAPIResponse(PaginatedAPIResponse):
    apps: List[ResponseApp]
