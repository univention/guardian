# Copyright (C) 2023 Univention GmbH
#
# SPDX-License-Identifier: AGPL-3.0-only

from dataclasses import dataclass
from typing import Iterable, Optional

from ..models.policies import Permission


@dataclass(frozen=True)
class GetPermissionAPIResult:
    target_id: str
    permissions: Iterable[Permission]


@dataclass(frozen=True)
class GetPermissionAPIResponse:
    target_permissions: Iterable[GetPermissionAPIResult]
    general_permissions: Optional[Iterable[Permission]]
