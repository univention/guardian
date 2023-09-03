# Copyright (C) 2023 Univention GmbH
#
# SPDX-License-Identifier: AGPL-3.0-only

from abc import ABC, abstractmethod
from typing import Any, Generic, Optional, Tuple, TypeVar

from guardian_lib.ports import BasePort

from ..models.condition import Condition, ConditionGetQuery, ConditionsGetQuery
from .base import BasePersistencePort


class ConditionPersistencePort(
    BasePersistencePort[Condition, ConditionGetQuery, ConditionsGetQuery], ABC
):
    ...


APIGetSingleRequestObject = TypeVar("APIGetSingleRequestObject")
APIGetSingleResponseObject = TypeVar("APIGetSingleResponseObject")
APIGetMultipleRequestObject = TypeVar("APIGetMultipleRequestObject")
APIGetMultipleResponseObject = TypeVar("APIGetMultipleResponseObject")
APICreateRequestObject = TypeVar("APICreateRequestObject")
APIEditRequestObject = TypeVar("APIEditRequestObject")


class ConditionAPIPort(
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
    async def transform_exception(self, exc: Exception):
        ...  # pragma: no cover

    @abstractmethod
    async def to_obj_get_single(
        self, api_request: APIGetSingleRequestObject
    ) -> ConditionGetQuery:
        ...  # pragma: no cover

    @abstractmethod
    async def to_api_get_single_response(
        self, obj: Condition
    ) -> APIGetSingleResponseObject:
        ...  # pragma: no cover

    @abstractmethod
    async def to_obj_get_multiple(
        self, api_request: APIGetMultipleRequestObject
    ) -> ConditionsGetQuery:
        ...  # pragma: no cover

    @abstractmethod
    async def to_api_get_multiple_response(
        self,
        objs: list[Condition],
        query_offset: int,
        query_limit: Optional[int],
        total_count: int,
    ) -> APIGetMultipleResponseObject:
        ...  # pragma: no cover

    @abstractmethod
    async def to_obj_create(self, api_request: APICreateRequestObject) -> Condition:
        ...  # pragma: no cover

    @abstractmethod
    async def to_obj_edit(
        self, api_request: APIEditRequestObject
    ) -> Tuple[ConditionGetQuery, dict[str, Any]]:
        ...  # pragma: no cover
