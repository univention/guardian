# Copyright (C) 2023 Univention GmbH
#
# SPDX-License-Identifier: AGPL-3.0-only

"""
Proposed layout for the app-related ports
"""

from abc import ABC, abstractmethod
from typing import Generic, Optional, TypeVar

from ..models.app import App, AppCreateQuery, AppGetQuery, Apps
from .base import BasePort

AppAPICreateRequestObject = TypeVar("AppAPICreateRequestObject")
AppAPICreateResponseObject = TypeVar("AppAPICreateResponseObject")

AppAPIGetRequestObject = TypeVar("AppAPIGetRequestObject")
AppAPIGetResponseObject = TypeVar("AppAPIGetResponseObject")

###############################################################################
#                                                                             #
#  Incoming ports                                                             #
#                                                                             #
###############################################################################


class AppAPIPort(
    BasePort,
    ABC,
    Generic[
        AppAPICreateRequestObject,
        AppAPICreateResponseObject,
        AppAPIGetRequestObject,
        AppAPIGetResponseObject,
    ],
):
    @abstractmethod
    async def to_app_create(
        self, api_request: AppAPICreateRequestObject
    ) -> AppCreateQuery:
        raise NotImplementedError  # pragma: no cover

    @abstractmethod
    async def to_api_create_response(
        self, app_result: App
    ) -> AppAPICreateResponseObject:
        raise NotImplementedError  # pragma: no cover

    @abstractmethod
    async def to_app_get(self, api_request: AppAPIGetRequestObject) -> AppGetQuery:
        raise NotImplementedError  # pragma: no cover

    @abstractmethod
    async def to_api_get_response(
        self, app_result: App | None
    ) -> AppAPIGetResponseObject | None:
        raise NotImplementedError  # pragma: no cover


###############################################################################
#                                                                             #
#  Outgoing ports                                                             #
#                                                                             #
###############################################################################


class AppPersistencePort(BasePort, ABC):
    @abstractmethod
    async def create(
        self,
        app: App,
    ) -> App:
        raise NotImplementedError  # pragma: no cover

    @abstractmethod
    async def read_one(
        self,
        query: AppGetQuery,
    ) -> App | None:
        raise NotImplementedError  # pragma: no cover

    @abstractmethod
    async def read_many(
        self,
        query_offset: Optional[int] = None,
        query_limit: Optional[int] = None,
    ) -> Apps:
        raise NotImplementedError  # pragma: no cover

    @abstractmethod
    async def update(
        self,
        app: App,
    ) -> App:
        raise NotImplementedError  # pragma: no cover
