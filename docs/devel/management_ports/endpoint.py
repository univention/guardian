"""
Proposed layout for the role-capability-mapping ports/models
"""

from dataclasses import dataclass
from typing import Optional

from .base import (
    BasePort,
    NamespacedObject,
    NamespacedPersistenceObject,
    ResponseObject,
)

###############################################################################
#                                                                             #
#  Models                                                                     #
#                                                                             #
###############################################################################


class CustomEndpoint(NamespacedPersistenceObject):
    code: bytes


class CustomEndpointDiff(NamespacedPersistenceObject):
    authorization_url: str  # Endpoint in the authz API
    old_code: Optional[bytes]  # Will be empty if code was just created
    new_code: bytes


class ResponseCustomEndpoint(NamespacedObject, ResponseObject):
    authorization_url: str  # Endpoint in the authz API that was created


@dataclass
class CustomEndpointAPIResponse:
    endpoint: ResponseCustomEndpoint


###############################################################################
#                                                                             #
#  Incoming ports                                                             #
#                                                                             #
###############################################################################


class CustomEndpointAPIPort(BasePort):
    async def create(
        self,
        app_name: str,
        namespace_name: str,
        endpoint_name: str,
        code: bytes,
    ) -> CustomEndpointAPIResponse:
        pass

    async def update(
        app_name: str,
        namespace_name: str,
        endpoint_name: str,
        code: bytes,
    ) -> CustomEndpointAPIResponse:
        pass


###############################################################################
#                                                                             #
#  Outgoing ports                                                             #
#                                                                             #
###############################################################################


class CustomEndpointPersistencePort(BasePort):
    async def create(
        self,
        endpoint: CustomEndpoint,
    ) -> CustomEndpointDiff:
        pass

    async def update(
        self,
        endpoint: CustomEndpoint,
    ) -> CustomEndpointDiff:
        pass
