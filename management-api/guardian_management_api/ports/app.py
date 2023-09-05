# Copyright (C) 2023 Univention GmbH
#
# SPDX-License-Identifier: AGPL-3.0-only

"""
Proposed layout for the app-related ports
"""

from abc import ABC, abstractmethod
from typing import Generic, List, Optional, TypeVar

from guardian_lib.ports import BasePort

from ..models.app import (
    App,
    AppCreateQuery,
    AppEditQuery,
    AppGetQuery,
    AppsGetQuery,
)
from .base import BasePersistencePort

AppAPICreateRequestObject = TypeVar("AppAPICreateRequestObject")
AppAPICreateResponseObject = TypeVar("AppAPICreateResponseObject")

AppAPIGetRequestObject = TypeVar("AppAPIGetRequestObject")
AppAPIGetResponseObject = TypeVar("AppAPIGetResponseObject")

AppsAPIGetRequestObject = TypeVar("AppsAPIGetRequestObject")
AppsAPIGetResponseObject = TypeVar("AppsAPIGetResponseObject")

AppAPIEditRequestObject = TypeVar("AppAPIEditRequestObject")
AppAPIEditResponseObject = TypeVar("AppAPIEditResponseObject")

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
        AppsAPIGetRequestObject,
        AppsAPIGetResponseObject,
        AppAPIEditRequestObject,
        AppAPIEditResponseObject,
    ],
):
    @abstractmethod
    async def transform_exception(self, exc: Exception) -> Exception:
        raise NotImplementedError  # pragma: no cover

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
    async def to_app_edit(self, api_request: AppAPIEditRequestObject) -> AppEditQuery:
        raise NotImplementedError  # pragma: no cover

    @abstractmethod
    async def to_api_edit_response(self, app_result: App) -> AppAPIEditResponseObject:
        raise NotImplementedError  # pragma: no cover

    @abstractmethod
    async def to_app_get(self, api_request: AppAPIGetRequestObject) -> AppGetQuery:
        raise NotImplementedError  # pragma: no cover

    @abstractmethod
    async def to_api_get_response(self, app_result: App) -> AppAPIGetResponseObject:
        raise NotImplementedError  # pragma: no cover

    @abstractmethod
    async def to_apps_get(self, api_request: AppsAPIGetRequestObject) -> AppsGetQuery:
        raise NotImplementedError  # pragma: no cover

    @abstractmethod
    async def to_api_apps_get_response(
        self,
        apps: List[App],
        query_offset: int,
        query_limit: Optional[int],
        total_count: int,
    ) -> AppsAPIGetResponseObject:
        raise NotImplementedError  # pragma: no cover


###############################################################################
#                                                                             #
#  Outgoing ports                                                             #
#                                                                             #
###############################################################################


class AppPersistencePort(BasePersistencePort[App, AppGetQuery, AppsGetQuery], ABC):
    ...
