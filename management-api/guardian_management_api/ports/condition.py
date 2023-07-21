# Copyright (C) 2023 Univention GmbH
#
# SPDX-License-Identifier: AGPL-3.0-only

"""
Proposed layout for condition ports/models
"""

from abc import abstractmethod
from dataclasses import dataclass
from typing import List, Optional

from ..models.base import (
    NamespacedPersistenceObject,
    NamespacedResponseObject,
    QueryResponse,
)
from .base import (
    BasePort,
)

###############################################################################
#                                                                             #
#  Models                                                                     #
#                                                                             #
###############################################################################


class Condition(NamespacedPersistenceObject):
    parameter_names: Optional[List[str]]
    documentation_string: Optional[str]


class ConditionQuery(QueryResponse):
    conditions: List[Condition]


class ConditionDiff(NamespacedPersistenceObject):
    old_code: Optional[bytes]  # Will be empty if code was just created
    new_code: bytes
    parameter_names: List[str]
    documentation_string: str


class ResponseCondition(NamespacedResponseObject):
    parameter_names: List[str]
    documentation_string: str


@dataclass
class ConditionAPIResponse:
    condition: ResponseCondition


@dataclass
class ConditionsListAPIResponse:
    conditions: List[ResponseCondition]


###############################################################################
#                                                                             #
#  Incoming Ports                                                             #
#                                                                             #
###############################################################################


class ConditionAPIPort(BasePort):
    @abstractmethod
    async def create(
        self,
        app_name: str,
        namespace_name: str,
        condition_name: str,
        code: bytes,
        parameter_names: List[str],
        documentation_string: str,
    ) -> ConditionAPIResponse:
        pass

    @abstractmethod
    async def read_one(
        self,
        app_name: str,
        namespace_name: str,
        endpoint_name: str,
    ) -> ConditionAPIResponse:
        pass

    @abstractmethod
    async def read_many(
        self,
        app_name: Optional[str] = None,
        namespace_name: Optional[str] = None,
        pagination_offset: Optional[int] = None,
        pagination_limit: Optional[int] = None,
    ) -> ConditionsListAPIResponse:
        pass

    @abstractmethod
    async def update(
        self,
        app_name: str,
        namespace_name: str,
        condition_name: str,
        code: Optional[bytes] = None,
        parameter_names: Optional[List[str]] = None,
        documentation_string: Optional[str] = None,
    ) -> ConditionAPIResponse:
        pass


###############################################################################
#                                                                             #
#  Outgoing Ports                                                             #
#                                                                             #
###############################################################################


class ConditionPersistencePort(BasePort):
    @abstractmethod
    async def create(
        self,
        Condition: Condition,
    ) -> ConditionDiff:
        pass

    @abstractmethod
    async def read_one(
        self,
        app_name: str,
        namespace_name: str,
        condition_name: str,
    ) -> Condition:
        pass

    @abstractmethod
    async def read_many(
        self,
        app_name: Optional[str] = None,
        namespace_name: Optional[str] = None,
        query_offset: Optional[int] = None,
        query_limit: Optional[int] = None,
    ) -> List[Condition]:
        pass

    @abstractmethod
    async def update(
        self,
        condition: Condition,
    ) -> ConditionDiff:
        pass
