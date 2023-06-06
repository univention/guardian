"""
Proposed layout for the namespace ports/models
"""

from dataclasses import dataclass
from typing import List, Optional

from .base import BasePort, PaginatedAPIResponse, QueryResponse, ResponseObject

###############################################################################
#                                                                             #
#  Models                                                                     #
#                                                                             #
###############################################################################


@dataclass
class Namespace:
    app_name: str
    name: str
    display_name: Optional[str]


class NamespaceQuery(QueryResponse):
    namespaces: List[Namespace]


# We're intentionally not tying this to Namespace,
# because we'd like to make sure changes to the persistence layer don't
# accidentally affect the response layer.
class ResponseNamespace(ResponseObject):
    app_name: str
    name: str
    display_name: Optional[str]


@dataclass
class NamespaceAPIResponse:
    namespace: ResponseNamespace


class NamespacesListAPIResponse(PaginatedAPIResponse):
    namespaces: List[ResponseNamespace]


###############################################################################
#                                                                             #
#  Incoming ports                                                             #
#                                                                             #
###############################################################################


class NamespaceAPIPort(BasePort):
    async def create(
        self,
        app_name: str,
        namespace_name: str,
        display_name: Optional[str] = None,
    ) -> NamespaceAPIResponse:
        pass

    async def read_one(
        self,
        app_name: str,
        namespace_name: str,
    ) -> NamespaceAPIResponse:
        pass

    async def read_many(
        self,
        app_name: Optional[str] = None,
        namespace_name: Optional[str] = None,
        pagination_offset: Optional[int] = None,
        pagination_limit: Optional[int] = None,
    ) -> NamespacesListAPIResponse:
        pass

    async def update(
        self,
        app_name: str,
        namespace_name: str,
        display_name: str,
    ) -> NamespaceAPIResponse:
        pass


###############################################################################
#                                                                             #
#  Outgoing ports                                                             #
#                                                                             #
###############################################################################


class NamespacePersistencePort(BasePort):
    async def create(
        self,
        namespace: Namespace,
    ) -> Namespace:
        pass

    async def read_one(
        self,
        app_name: str,
        namespace_name: str,
    ) -> Namespace:
        pass

    async def read_many(
        self,
        app_name: Optional[str] = None,
        namespace_name: Optional[str] = None,
        query_offset: Optional[int] = None,
        query_limit: Optional[int] = None,
    ) -> NamespaceQuery:
        pass

    async def update(
        self,
        namespace: Namespace,
    ) -> Namespace:
        pass
