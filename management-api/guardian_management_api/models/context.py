# Copyright (C) 2023 Univention GmbH
#
# SPDX-License-Identifier: AGPL-3.0-only

from dataclasses import dataclass
from typing import Optional

from .base import PaginationRequest
from .flags import Flag


@dataclass
class Context:
    app_name: str
    namespace_name: str
    name: str
    display_name: Optional[str] = None
    flags: Flag = Flag.NONE


@dataclass(frozen=True)
class ContextGetQuery:
    app_name: str
    namespace_name: str
    name: str


@dataclass(frozen=True)
class ContextsGetQuery:
    pagination: PaginationRequest
    app_name: Optional[str] = None
    namespace_name: Optional[str] = None
