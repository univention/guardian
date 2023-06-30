# Copyright (C) 2023 Univention GmbH
#
# SPDX-License-Identifier: AGPL-3.0-only

"""
Proposed layout for the app-related ports
"""

from dataclasses import dataclass
from typing import List, Optional

from .base import BasePort, PaginatedAPIResponse, QueryResponse, ResponseObject
from .role import ResponseRole

###############################################################################
#                                                                             #
#  Models                                                                     #
#                                                                             #
###############################################################################


@dataclass
class App:
    name: str
    display_name: Optional[str]


class AppQuery(QueryResponse):
    apps: List[App]


# We're intentionally not tying this to App,
# because we'd like to make sure changes to the persistence layer don't
# accidentally affect the response layer.
class ResponseApp(ResponseObject):
    name: str
    display_name: Optional[str]
    app_admin: Optional[ResponseRole]


@dataclass
class AppAPIResponse:
    app: ResponseApp


class AppsListAPIResponse(PaginatedAPIResponse):
    apps: List[ResponseApp]


###############################################################################
#                                                                             #
#  Incoming ports                                                             #
#                                                                             #
###############################################################################


class AppAPIPort(BasePort):
    async def create(
        self,
        app_name: str,
        display_name: Optional[str] = None,
    ) -> AppAPIResponse:
        pass

    async def create_with_admin(
        self,
        app_name: str,
        display_name: Optional[str] = None,
    ) -> AppAPIResponse:
        # This will also need to use the RolePersistencePort,
        # in order to create an administrator
        pass

    async def read_one(
        self,
        app_name: str,
    ) -> AppAPIResponse:
        pass

    async def read_many(
        self,
        pagination_offset: Optional[int] = None,
        pagination_limit: Optional[int] = None,
    ) -> AppsListAPIResponse:
        pass

    async def update(
        self,
        app_name: str,
        display_name: str,
    ) -> AppAPIResponse:
        pass


###############################################################################
#                                                                             #
#  Outgoing ports                                                             #
#                                                                             #
###############################################################################


class AppPersistencePort(BasePort):
    async def create(
        self,
        app: App,
    ) -> App:
        pass

    async def read_one(
        self,
        app_name: str,
    ) -> App:
        pass

    async def read_many(
        self,
        query_offset: Optional[int] = None,
        query_limit: Optional[int] = None,
    ) -> AppQuery:
        pass

    async def update(
        self,
        app: App,
    ) -> App:
        pass
