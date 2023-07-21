# Copyright (C) 2023 Univention GmbH
#
# SPDX-License-Identifier: AGPL-3.0-only

"""
Proposed layout for context ports/models
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


class Context(NamespacedPersistenceObject):
    ...


class ContextQuery(QueryResponse):
    contexts: List[Context]


class ResponseContext(NamespacedResponseObject):
    ...


@dataclass
class ContextAPIResponse:
    context: ResponseContext


class ContextsListAPIResponse(PaginatedAPIResponse):
    contexts: List[ResponseContext]


###############################################################################
#                                                                             #
#  Incoming ports                                                             #
#                                                                             #
###############################################################################


class ContextAPIPort(BasePort):
    @abstractmethod
    def create(
        self,
        app_name: str,
        namespace_name: str,
        context_name: str,
        display_name: Optional[str] = None,
    ) -> ContextAPIResponse:
        pass

    @abstractmethod
    def read_one(
        self,
        app_name: str,
        namespace_name: str,
        context_name: str,
    ) -> ContextAPIResponse:
        pass

    @abstractmethod
    def read_many(
        self,
        app_name: Optional[str] = None,
        namespace_name: Optional[str] = None,
        pagination_offset: Optional[int] = None,
        pagination_limit: Optional[int] = None,
    ) -> ContextsListAPIResponse:
        pass

    @abstractmethod
    def update(
        self,
        app_name: str,
        namespace_name: str,
        context_name: str,
        display_name: str,
    ) -> ContextAPIResponse:
        pass


###############################################################################
#                                                                             #
#  Outgoing ports                                                             #
#                                                                             #
###############################################################################


class ContextPersistencePort(BasePort):
    @abstractmethod
    async def create(
        self,
        context: Context,
    ) -> Context:
        pass

    @abstractmethod
    async def read_one(
        self,
        app_name: str,
        namespace_name: str,
        context_name: str,
    ) -> Context:
        pass

    @abstractmethod
    async def read_many(
        self,
        app_name: Optional[str] = None,
        namespace_name: Optional[str] = None,
        query_offset: Optional[int] = None,
        query_limit: Optional[int] = None,
    ) -> ContextQuery:
        pass

    @abstractmethod
    async def update(
        self,
        context: Context,
    ) -> Context:
        pass
