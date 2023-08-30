from dataclasses import dataclass
from typing import Optional

from guardian_management_api.models.base import PaginationRequest


@dataclass(frozen=True)
class Permission:
    app_name: str
    namespace_name: str
    name: str
    display_name: Optional[str] = None


@dataclass(frozen=True)
class PermissionGetQuery:
    app_name: str
    namespace_name: str
    name: str


@dataclass(frozen=True)
class PermissionsGetQuery:
    pagination: PaginationRequest
