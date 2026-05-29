# Copyright (C) 2023 Univention GmbH
#
# SPDX-License-Identifier: AGPL-3.0-only
from dataclasses import dataclass
from enum import StrEnum
from typing import Any, Optional

from .base import PaginationRequest
from .condition import ConditionParameterType
from .permission import Permission


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


@dataclass(frozen=True)
class CapabilityReference:
    """Identifier-only handle for a capability, used wherever a full
    capability is not needed (e.g. ``Role.capabilities``)."""

    app_name: str
    namespace_name: str
    name: str


@dataclass
class Capability:
    app_name: str
    namespace_name: str
    name: str
    display_name: Optional[str]
    permissions: list[Permission]
    relation: CapabilityConditionRelation
    conditions: list[ParametrizedCondition]
    is_builtin: bool = False

    def to_reference(self) -> CapabilityReference:
        return CapabilityReference(
            app_name=self.app_name,
            namespace_name=self.namespace_name,
            name=self.name,
        )


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
