# Copyright (C) 2023 Univention GmbH
#
# SPDX-License-Identifier: AGPL-3.0-only

"""
Proposed layout for the role-capability-mapping ports/models
"""

from abc import abstractmethod
from dataclasses import dataclass
from typing import Optional

from ..models.base import (
    NamespacedObject,
    NamespacedPersistenceObject,
    ResponseObject,
)
from .base import (
    BasePort,
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
    @abstractmethod
    async def create(
        self,
        app_name: str,
        namespace_name: str,
        endpoint_name: str,
        code: bytes,
    ) -> CustomEndpointAPIResponse:
        pass

    @abstractmethod
    async def update(
        self,
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
    @abstractmethod
    async def create(
        self,
        endpoint: CustomEndpoint,
    ) -> CustomEndpointDiff:
        pass

    @abstractmethod
    async def update(
        self,
        endpoint: CustomEndpoint,
    ) -> CustomEndpointDiff:
        pass
