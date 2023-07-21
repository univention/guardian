# Copyright (C) 2023 Univention GmbH
#
# SPDX-License-Identifier: AGPL-3.0-only

"""
Proposed layout for the role-capability-mapping ports/models
"""

from abc import abstractmethod
from dataclasses import dataclass
from enum import StrEnum
from typing import Dict, List, Optional, Union

from .base import BasePort

###############################################################################
#                                                                             #
#  Models                                                                     #
#                                                                             #
###############################################################################

# /start persistence models

# The persistence models proposed here is loosely based on:
#
# https://git.knut.univention.de/univention/ucsschool/-/blob/5.0/doc/devel/ram/concept_proposal.md#role-capability-mapping
#
# The models for these should be tentative and subject to change as we figure
# out how to store the role-capability-mapping for use in OPA.
# Let's discuss, but not get too deep into the weeds on this part of the implementation.


# When storing a NamespacedMappingObject, we should store them as strings
# with a separator -- e.g., "foo:bar:baz" -- rather than objects, because it
# may be easier to filter.
@dataclass
class NamespacedMappingObject:
    app_name: str
    namespace_name: str
    name: str


class MappingPermission(NamespacedMappingObject):
    ...


class MappingRole(NamespacedMappingObject):
    ...


@dataclass
class MappingCondition:
    name: str  # This corresponds to the function name that will be called
    parameters: Dict[
        str, Union[str, int, float, bool]
    ]  # What we can reliably parse from javascript


class MappingRelation(StrEnum):
    AND = "AND"
    OR = "OR"


@dataclass
class MappingCapability:
    conditions: List[MappingCondition]
    relation: MappingRelation
    permissions: List[
        MappingPermission
    ]  # The outgoing port should store as app:namespace:name


@dataclass
class Mapping:
    role: MappingRole  # The outgoing port should store as app:namespace:name
    app_name: str
    namespace_name: str
    capabilities: List[MappingCapability]


# /end outgoing models


# Keep this separate from the storage objects, in case we change the format
# later
@dataclass
class NamespacedAPIMappingObject:
    app_name: str
    namespace_name: str
    name: str


class APIMappingRole(NamespacedMappingObject):
    ...


class APIMappingCondition(NamespacedMappingObject):
    ...


class APIMappingPermission(NamespacedMappingObject):
    ...


@dataclass
class APIMapping:
    role: APIMappingRole
    conditions: List[APIMappingCondition]
    relation: str
    permissions: List[APIMappingPermission]


@dataclass
class RoleCapabilityMappingAPIResponse:
    mappings: List[APIMapping]


class DeletedRoleCapabilityMappingAPIResponse:
    deleted_mappings: List[APIMapping]


###############################################################################
#                                                                             #
#  Incoming ports                                                             #
#                                                                             #
###############################################################################


class RoleCapabilityMappingAPIPort(BasePort):
    @abstractmethod
    async def read(self) -> RoleCapabilityMappingAPIResponse:
        pass

    @abstractmethod
    async def read_namespace(
        self,
        app_name: str,
        namespace_name: str,
    ) -> RoleCapabilityMappingAPIResponse:
        pass

    @abstractmethod
    async def update(
        self,
        mappings: List[APIMapping],
    ) -> RoleCapabilityMappingAPIResponse:
        pass

    @abstractmethod
    async def update_namespace(
        self, app_name: str, namespace_name: str, mappings: List[APIMapping]
    ) -> RoleCapabilityMappingAPIResponse:
        pass

    @abstractmethod
    async def delete_namespace(
        self,
        app_name: str,
        namespace_name: str,
    ) -> DeletedRoleCapabilityMappingAPIResponse:
        # We should return what mappings were deleted,
        # as an additional verification for the client
        pass


###############################################################################
#                                                                             #
#  Outgoing ports                                                             #
#                                                                             #
###############################################################################


class RoleCapabilityMappingPersistencePort(BasePort):
    # Here, the namespace acts as a filter;
    # otherwise, everything is returned.
    @abstractmethod
    async def read(
        self,
        app_name: Optional[str] = None,
        namespace_name: Optional[str] = None,
    ) -> List[Mapping]:
        pass

    # Discussion point: do we need to distinguish between an update and a create here?
    # I can see some implementations of an adapter where we might,
    # but if we're doing this as a file, it might not make sense.
    # Perhaps leave it up to the adapter to figure out whether it needs to handle
    # "already exists" errors?
    @abstractmethod
    async def write(
        self,
        mappings: List[Mapping],
    ) -> List[Mapping]:
        pass

    # A delete for a namespace is just passing an empty list
    @abstractmethod
    async def write_namespace(
        self,
        app_name: str,
        namespace_name: str,
        mappings: List[Mapping],
    ) -> List[Mapping]:
        pass
