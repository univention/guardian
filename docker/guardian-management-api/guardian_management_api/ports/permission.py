# Copyright (C) 2023 Univention GmbH
#
# SPDX-License-Identifier: AGPL-3.0-only
"""
Layout for the permission-related ports
"""

from abc import ABC, abstractmethod
from typing import Any, Generic, Optional, TypeVar

from guardian_lib.ports import BasePort

from ..models.permission import (
    Permission,
    PermissionCreateQuery,
    PermissionGetQuery,
    PermissionsGetQuery,
)
from .base import BasePersistencePort

PermissionAPIGetSingleRequestObject = TypeVar("PermissionAPIGetSingleRequestObject")
PermissionAPIGetSingleResponseObject = TypeVar("PermissionAPIGetSingleResponseObject")
PermissionAPIGetMultipleRequestObject = TypeVar("PermissionAPIGetMultipleRequestObject")
PermissionAPIGetMultipleResponseObject = TypeVar(
    "PermissionAPIGetMultipleResponseObject"
)
PermissionAPICreateRequestObject = TypeVar("PermissionAPICreateRequestObject")
PermissionAPIEditRequestObject = TypeVar("PermissionAPIEditRequestObject")


###############################################################################
#                                                                             #
#  Incoming ports                                                             #
#                                                                             #
###############################################################################


class PermissionAPIPort(
    BasePort,
    ABC,
    Generic[
        PermissionAPIGetSingleRequestObject,
        PermissionAPIGetSingleResponseObject,
        PermissionAPIGetMultipleRequestObject,
        PermissionAPIGetMultipleResponseObject,
        PermissionAPICreateRequestObject,
        PermissionAPIEditRequestObject,
    ],
):
    @abstractmethod
    async def transform_exception(self, exc: Exception):
        ...  # pragma: no cover

    @abstractmethod
    async def to_obj_create(
        self, api_request: PermissionAPICreateRequestObject
    ) -> PermissionCreateQuery:
        ...  # pragma: no cover

    @abstractmethod
    async def to_obj_edit(
        self, api_request: PermissionAPIEditRequestObject
    ) -> tuple[PermissionGetQuery, dict[str, Any]]:
        ...  # pragma: no cover

    @abstractmethod
    async def to_api_get_single_response(
        self, permission_result: Permission
    ) -> PermissionAPIGetSingleResponseObject:
        ...  # pragma: no cover

    @abstractmethod
    async def to_obj_get_single(
        self, api_request: PermissionAPIGetSingleRequestObject
    ) -> PermissionGetQuery:
        ...  # pragma: no cover

    @abstractmethod
    async def to_obj_get_multiple(
        self, api_request: PermissionAPIGetMultipleRequestObject
    ) -> PermissionsGetQuery:
        ...  # pragma: no cover

    @abstractmethod
    async def to_api_get_multiple_response(
        self,
        objs: list[Permission],
        query_offset: int,
        query_limit: Optional[int],
        total_count: int,
    ) -> PermissionAPIGetMultipleResponseObject:
        ...  # pragma: no cover


###############################################################################
#                                                                             #
#  Outgoing ports                                                             #
#                                                                             #
###############################################################################


class PermissionPersistencePort(
    BasePersistencePort[Permission, PermissionGetQuery, PermissionsGetQuery], ABC
):
    ...
