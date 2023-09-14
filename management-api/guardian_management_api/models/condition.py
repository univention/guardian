# Copyright (C) 2023 Univention GmbH
#
# SPDX-License-Identifier: AGPL-3.0-only

from dataclasses import dataclass, field
from enum import StrEnum
from typing import Optional

from guardian_management_api.models.base import PaginationRequest


class ConditionParameterType(StrEnum):
    ANY = "ANY"
    STRING = "STRING"
    FLOAT = "FLOAT"
    INT = "INT"
    BOOLEAN = "BOOLEAN"
    ROLE = "ROLE"
    CONTEXT = "CONTEXT"


@dataclass
class ConditionParameter:
    name: str
    value_type: ConditionParameterType


@dataclass
class Condition:
    app_name: str
    namespace_name: str
    name: str
    code: bytes
    display_name: Optional[str] = None
    documentation: Optional[str] = None
    parameters: list[ConditionParameter] = field(default_factory=list)


@dataclass(frozen=True)
class ConditionGetQuery:
    app_name: str
    namespace_name: str
    name: str


@dataclass(frozen=True)
class ConditionsGetQuery:
    pagination: PaginationRequest
    app_name: Optional[str] = None
    namespace_name: Optional[str] = None
