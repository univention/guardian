# Copyright (C) 2023 Univention GmbH
#
# SPDX-License-Identifier: AGPL-3.0-only

from abc import ABC, abstractmethod
from typing import Generic, List, Optional, TypeVar

from ..models.namespace import (
    Namespace,
    NamespaceCreateQuery,
    NamespaceEditQuery,
    NamespaceGetQuery,
    NamespacesGetQuery,
)
from ..models.routers.base import GetByAppRequest
from ..models.routers.namespace import (
    NamespaceEditRequest,
    NamespacesGetRequest,
)
from .base import BasePersistencePort, BasePort

NamespaceAPICreateRequestObject = TypeVar("NamespaceAPICreateRequestObject")
NamespaceAPICreateResponseObject = TypeVar("NamespaceAPICreateResponseObject")

NamespaceAPIGetRequestObject = TypeVar("NamespaceAPIGetRequestObject")
NamespaceAPIGetResponseObject = TypeVar("NamespaceAPIGetResponseObject")

NamespacesAPIGetRequestObject = TypeVar("NamespacesAPIGetRequestObject")
NamespacesAPIGetResponseObject = TypeVar("NamespacesAPIGetResponseObject")

NamespaceAPIEditRequestObject = TypeVar("NamespaceAPIEditRequestObject")
NamespaceAPIEditResponseObject = TypeVar("NamespaceAPIEditResponseObject")

NamespacesByAppnameAPIGetRequestObject = TypeVar(
    "NamespacesByAppnameAPIGetRequestObject"
)
NamespacesByAppnameAPIGetResponseObject = TypeVar(
    "NamespacesByAppnameAPIGetResponseObject"
)

###############################################################################
#                                                                             #
#  Incoming ports                                                             #
#                                                                             #
###############################################################################


class NamespaceAPIPort(
    BasePort,
    ABC,
    Generic[
        NamespaceAPICreateRequestObject,
        NamespaceAPICreateResponseObject,
        NamespaceAPIGetRequestObject,
        NamespaceAPIGetResponseObject,
        NamespacesAPIGetRequestObject,
        NamespacesAPIGetResponseObject,
        NamespaceAPIEditRequestObject,
        NamespaceAPIEditResponseObject,
        NamespacesByAppnameAPIGetRequestObject,
        NamespacesByAppnameAPIGetResponseObject,
    ],
):
    @abstractmethod
    async def transform_exception(self, exc: Exception) -> Exception:
        raise NotImplementedError  # pragma: no cover

    @abstractmethod
    async def to_namespace_create(
        self, api_request: NamespaceAPICreateRequestObject
    ) -> NamespaceCreateQuery:
        raise NotImplementedError  # pragma: no cover

    @abstractmethod
    async def to_api_create_response(
        self, namespace_result: Namespace
    ) -> NamespaceAPICreateResponseObject:
        raise NotImplementedError  # pragma: no cover

    @abstractmethod
    async def to_namespace_edit(
        self, api_request: NamespaceEditRequest
    ) -> NamespaceEditQuery:
        raise NotImplementedError  # pragma: no cover

    @abstractmethod
    async def to_api_edit_response(
        self, namespace_result: Namespace
    ) -> NamespaceAPIEditResponseObject:
        raise NotImplementedError  # pragma: no cover

    @abstractmethod
    async def to_namespace_get(
        self, api_request: NamespaceAPIGetRequestObject
    ) -> NamespaceGetQuery:
        raise NotImplementedError  # pragma: no cover

    @abstractmethod
    async def to_api_get_response(
        self, namespace_result: Namespace
    ) -> NamespaceAPIGetResponseObject:
        raise NotImplementedError  # pragma: no cover

    @abstractmethod
    async def to_namespaces_get(
        self, api_request: NamespacesGetRequest
    ) -> NamespacesGetQuery:
        raise NotImplementedError  # pragma: no cover

    @abstractmethod
    async def to_api_namespaces_get_response(
        self,
        namespaces: List[Namespace],
        query_offset: int,
        query_limit: Optional[int],
        total_count: int,
    ) -> NamespacesAPIGetResponseObject:
        raise NotImplementedError  # pragma: no cover

    @abstractmethod
    async def to_namespaces_by_appname_get(
        self, api_request: GetByAppRequest
    ) -> NamespacesGetQuery:
        raise NotImplementedError  # pragma: no cover


###############################################################################
#                                                                             #
#  Outgoing ports                                                             #
#                                                                             #
###############################################################################


class NamespacePersistencePort(
    BasePersistencePort[Namespace, NamespaceGetQuery, NamespacesGetQuery], ABC
): ...
