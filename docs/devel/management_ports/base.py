"""
Shared classes for the ports/models implementations
"""

from abc import ABC
from dataclasses import dataclass
from typing import Optional

###############################################################################
#                                                                             #
#  Models                                                                     #
#                                                                             #
###############################################################################


@dataclass
class NamespacedObject:
    """Bare-bones representation of something that should be namespaced"""

    app_name: str
    namespace_name: str
    name: str


@dataclass
class NamespacedPersistenceObject(NamespacedObject):
    id: Optional[str]
    display_name: Optional[str]


@dataclass
class QueryResponse:
    query_offset: int
    query_limit: int
    total_count: int


@dataclass
class ResponseObject:
    resource_url: str


@dataclass
class PaginationResponse:
    offset: int
    limit: int
    total_count: int


@dataclass
class PaginatedAPIResponse:
    pagination: PaginationResponse


# We're intentionally not tying this to NamespacedPersistenceObject,
# because we'd like to make sure changes to the persistence layer don't
# accidentally affect the response layer.
class NamespacedResponseObject(NamespacedObject, ResponseObject):
    display_name: Optional[str]


###############################################################################
#                                                                             #
#  Ports                                                                      #
#                                                                             #
###############################################################################


class BasePort(ABC):
    # Placeholder for ideas like singleton configuration and settings
    ...
