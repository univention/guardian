# Copyright (C) 2023 Univention GmbH
#
# SPDX-License-Identifier: AGPL-3.0-only
from dataclasses import dataclass
from enum import StrEnum
from typing import Any, Optional

from guardian_management_api.models.base import PaginationRequest
from guardian_management_api.models.condition import ConditionParameterType
from guardian_management_api.models.permission import Permission
from guardian_management_api.models.role import Role


@dataclass
class CapabilityConditionParameter:
    name: str
    value: Any
    value_type: Optional[ConditionParameterType] = None


@dataclass
class ParametrizedCondition:
    app_name: str
    namespace_name: str
    name: str
    parameters: list[CapabilityConditionParameter]


class CapabilityConditionRelation(StrEnum):
    AND = "AND"
    OR = "OR"


@dataclass
class Capability:
    app_name: str
    namespace_name: str
    name: str
    display_name: Optional[str]
    role: Role
    permissions: list[Permission]
    relation: CapabilityConditionRelation
    conditions: list[ParametrizedCondition]


@dataclass(frozen=True)
class CapabilityGetQuery:
    app_name: str
    namespace_name: str
    name: str


@dataclass(frozen=True)
class CapabilitiesGetQuery:
    pagination: PaginationRequest
    app_name: Optional[str] = None
    namespace_name: Optional[str] = None


@dataclass(frozen=True)
class CapabilitiesByRoleQuery:
    pagination: PaginationRequest
    app_name: str
    namespace_name: str
    role_name: str
