# Copyright (C) 2023 Univention GmbH
#
# SPDX-License-Identifier: AGPL-3.0-only

"""
Shared classes for the ports/models implementations
"""

from dataclasses import dataclass
from typing import Generic, Iterable, Optional, TypeVar

###############################################################################
#                                                                             #
#  Models                                                                     #
#                                                                             #
###############################################################################


@dataclass(frozen=True)
class NamespacedObject:
    """Bare-bones representation of something that should be namespaced"""

    app_name: str
    namespace_name: str
    name: str


@dataclass(frozen=True)
class NamespacedPersistenceObject(NamespacedObject):
    id: Optional[str]
    display_name: Optional[str]


@dataclass(frozen=True)
class QueryResponse:
    query_offset: int
    query_limit: int
    total_count: int


@dataclass(frozen=True)
class ResponseObject:
    resource_url: str


@dataclass(frozen=True)
class PaginationResponse:
    offset: int
    limit: int
    total_count: int


@dataclass(frozen=True)
class PaginatedAPIResponse:
    pagination: PaginationResponse


# We're intentionally not tying this to NamespacedPersistenceObject,
# because we'd like to make sure changes to the persistence layer don't
# accidentally affect the response layer.
@dataclass(frozen=True)
class NamespacedResponseObject(NamespacedObject, ResponseObject):
    namespace_name: str
    display_name: Optional[str]


@dataclass(frozen=True)
class PaginationRequest:
    query_offset: int
    query_limit: Optional[int] = None


PersistenceObject = TypeVar("PersistenceObject")
PersistenceGetQuery = TypeVar("PersistenceGetQuery")
PersistenceGetManyQuery = TypeVar("PersistenceGetManyQuery")


@dataclass(frozen=True)
class PersistenceGetManyResult(Generic[PersistenceObject]):
    objects: Iterable[PersistenceObject]
    total_count: int
