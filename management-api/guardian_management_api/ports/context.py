# Copyright (C) 2023 Univention GmbH
#
# SPDX-License-Identifier: AGPL-3.0-only

from abc import ABC, abstractmethod
from typing import Any, Dict, Generic, List, Optional, Tuple, TypeVar

from guardian_lib.ports import BasePort

from ..models.context import (
    Context,
    ContextCreateQuery,
    ContextGetQuery,
    ContextsGetQuery,
)
from ..models.routers.context import ContextEditRequest
from .base import BasePersistencePort

ContextAPICreateRequestObject = TypeVar("ContextAPICreateRequestObject")
ContextAPICreateResponseObject = TypeVar("ContextAPICreateResponseObject")

ContextAPIGetRequestObject = TypeVar("ContextAPIGetRequestObject")
ContextAPIGetResponseObject = TypeVar("ContextAPIGetResponseObject")

ContextsAPIGetRequestObject = TypeVar("ContextsAPIGetRequestObject")
ContextsAPIGetResponseObject = TypeVar("ContextsAPIGetResponseObject")

ContextAPIEditRequestObject = TypeVar("ContextAPIEditRequestObject")
ContextAPIEditResponseObject = TypeVar("ContextAPIEditResponseObject")

###############################################################################
#                                                                             #
#  Incoming ports                                                             #
#                                                                             #
###############################################################################


class ContextAPIPort(
    BasePort,
    ABC,
    Generic[
        ContextAPICreateRequestObject,
        ContextAPICreateResponseObject,
        ContextAPIGetRequestObject,
        ContextAPIGetResponseObject,
        ContextsAPIGetRequestObject,
        ContextsAPIGetResponseObject,
        ContextAPIEditRequestObject,
        ContextAPIEditResponseObject,
    ],
):
    @abstractmethod
    async def transform_exception(self, exc: Exception) -> Exception:
        raise NotImplementedError  # pragma: no cover

    @abstractmethod
    async def to_context_create(
        self, api_request: ContextAPICreateRequestObject
    ) -> ContextCreateQuery:
        raise NotImplementedError  # pragma: no cover

    @abstractmethod
    async def to_api_create_response(
        self, context_result: Context
    ) -> ContextAPICreateResponseObject:
        raise NotImplementedError  # pragma: no cover

    @abstractmethod
    async def to_context_edit(
        self, api_request: ContextEditRequest
    ) -> Tuple[ContextGetQuery, Dict[str, Any]]:
        raise NotImplementedError  # pragma: no cover

    @abstractmethod
    async def to_api_edit_response(
        self, context_result: Context
    ) -> ContextAPIEditResponseObject:
        raise NotImplementedError  # pragma: no cover

    @abstractmethod
    async def to_context_get(
        self, api_request: ContextAPIGetRequestObject
    ) -> ContextGetQuery:
        raise NotImplementedError  # pragma: no cover

    @abstractmethod
    async def to_api_get_response(
        self, context_result: Context
    ) -> ContextAPIGetResponseObject:
        raise NotImplementedError  # pragma: no cover

    @abstractmethod
    async def to_contexts_get(
        self, api_request: ContextsAPIGetResponseObject
    ) -> ContextsGetQuery:
        raise NotImplementedError  # pragma: no cover

    @abstractmethod
    async def to_api_contexts_get_response(
        self,
        contexts: List[Context],
        query_offset: int,
        query_limit: Optional[int],
        total_count: int,
    ) -> ContextsAPIGetResponseObject:
        raise NotImplementedError  # pragma: no cover


###############################################################################
#                                                                             #
#  Outgoing ports                                                             #
#                                                                             #
###############################################################################


class ContextPersistencePort(
    BasePersistencePort[Context, ContextGetQuery, ContextsGetQuery], ABC
):
    ...
