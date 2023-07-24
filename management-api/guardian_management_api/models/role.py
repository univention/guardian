# Copyright (C) 2023 Univention GmbH
#
# SPDX-License-Identifier: AGPL-3.0-only

"""
Proposed layout for role ports/models
"""

from dataclasses import dataclass
from typing import List

from .base import (
    NamespacedPersistenceObject,
    NamespacedResponseObject,
    PaginatedAPIResponse,
    QueryResponse,
)


class Role(NamespacedPersistenceObject):
    ...


class RoleQuery(QueryResponse):
    roles: List[Role]


class ResponseRole(NamespacedResponseObject):
    ...


@dataclass(frozen=True)
class RoleAPIResponse(NamespacedResponseObject):
    role: ResponseRole


class RolesListAPIResponse(PaginatedAPIResponse):
    roles: List[ResponseRole]
