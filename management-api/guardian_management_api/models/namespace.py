# Copyright (C) 2023 Univention GmbH
#
# SPDX-License-Identifier: AGPL-3.0-only

from dataclasses import dataclass
from typing import Optional

from guardian_management_api.models.base import PaginationRequest


@dataclass(frozen=True)
class Namespace:
    app_name: str
    name: str
    display_name: Optional[str] = None


@dataclass(frozen=True)
class NamespaceGetQuery:
    app_name: str
    name: str


@dataclass(frozen=True)
class NamespacesGetQuery:
    pagination: PaginationRequest
    app_name: Optional[str] = None
