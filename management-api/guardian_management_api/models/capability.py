# Copyright (C) 2023 Univention GmbH
#
# SPDX-License-Identifier: AGPL-3.0-only
from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any, Optional

from .base import PaginationRequest
from .condition import ConditionParameterType
from .flags import Flag
from .permission import Permission
from .role import Role


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
    """
    Full capability. When passed as a reference (e.g. in ``Role.capabilities`` during
    create/update), only ``app_name``, ``namespace_name`` and ``name`` are required;
    the remaining fields are ignored by the persistence layer.
    """

    app_name: str
    namespace_name: str
    name: str
    display_name: Optional[str] = None
    permissions: list[Permission] = field(default_factory=list)
    relation: CapabilityConditionRelation = CapabilityConditionRelation.AND
    conditions: list[ParametrizedCondition] = field(default_factory=list)
    flags: Flag = Flag.NONE


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
