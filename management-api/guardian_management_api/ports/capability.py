# Copyright (C) 2023 Univention GmbH
#
# SPDX-License-Identifier: AGPL-3.0-only

from abc import ABC, abstractmethod
from typing import Generic, Optional, Union

from guardian_lib.ports import BasePort

from guardian_management_api.models.base import (
    APICreateRequestObject,
    APIEditRequestObject,
    APIGetMultipleRequestObject,
    APIGetMultipleResponseObject,
    APIGetSingleRequestObject,
    APIGetSingleResponseObject,
)
from guardian_management_api.models.capability import (
    CapabilitiesByRoleQuery,
    CapabilitiesGetQuery,
    Capability,
    CapabilityGetQuery,
)
from guardian_management_api.ports.base import BasePersistencePort


class CapabilityPersistencePort(
    BasePersistencePort[
        Capability,
        CapabilityGetQuery,
        Union[CapabilitiesGetQuery, CapabilitiesByRoleQuery],
    ],
    ABC,
):
    async def delete(self, query: CapabilityGetQuery) -> None:
        """
        Deletes the specified object from the persistent storage.

        :raises ObjectNotFoundError: If the object could not be found.
        :raises PersistenceError: For any other error during interaction with the persistence.
        """
        raise NotImplementedError  # pragma: no cover


class CapabilityAPIPort(
    BasePort,
    ABC,
    Generic[
        APIGetSingleRequestObject,
        APIGetSingleResponseObject,
        APIGetMultipleRequestObject,
        APIGetMultipleResponseObject,
        APICreateRequestObject,
        APIEditRequestObject,
    ],
):
    @abstractmethod
    async def transform_exception(self, exc: Exception): ...  # pragma: no cover

    @abstractmethod
    async def to_obj_get_single(
        self, api_request: APIGetSingleRequestObject
    ) -> CapabilityGetQuery: ...  # pragma: no cover

    @abstractmethod
    async def to_api_get_single_response(
        self, obj: Capability
    ) -> APIGetSingleResponseObject: ...  # pragma: no cover

    @abstractmethod
    async def to_obj_get_multiple(
        self, api_request: APIGetMultipleRequestObject
    ) -> CapabilitiesGetQuery | CapabilitiesByRoleQuery: ...  # pragma: no cover

    @abstractmethod
    async def to_api_get_multiple_response(
        self,
        objs: list[Capability],
        query_offset: int,
        query_limit: Optional[int],
        total_count: int,
    ) -> APIGetMultipleResponseObject: ...  # pragma: no cover

    @abstractmethod
    async def to_obj_create(
        self, api_request: APICreateRequestObject
    ) -> Capability: ...  # pragma: no cover

    @abstractmethod
    async def to_obj_edit(
        self, api_request: APIEditRequestObject
    ) -> Capability: ...  # pragma: no cover
