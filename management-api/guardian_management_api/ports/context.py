# Copyright (C) 2023 Univention GmbH
#
# SPDX-License-Identifier: AGPL-3.0-only

"""
Proposed layout for context ports/models
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
    def create(
        self,
        app_name: str,
        namespace_name: str,
        context_name: str,
        display_name: Optional[str] = None,
    ) -> ContextAPIResponse:
        pass

    def read_one(
        self,
        app_name: str,
        namespace_name: str,
        context_name: str,
    ) -> ContextAPIResponse:
        pass

    def read_many(
        self,
        app_name: Optional[str] = None,
        namespace_name: Optional[str] = None,
        pagination_offset: Optional[int] = None,
        pagination_limit: Optional[int] = None,
    ) -> ContextsListAPIResponse:
        pass

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
    async def create(
        self,
        context: Context,
    ) -> Context:
        pass

    async def read_one(
        self,
        app_name: str,
        namespace_name: str,
        context_name: str,
    ) -> Context:
        pass

    async def read_many(
        self,
        app_name: Optional[str] = None,
        namespace_name: Optional[str] = None,
        query_offset: Optional[int] = None,
        query_limit: Optional[int] = None,
    ) -> ContextQuery:
        pass

    async def update(
        self,
        context: Context,
    ) -> Context:
        pass
