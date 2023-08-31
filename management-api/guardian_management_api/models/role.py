from dataclasses import dataclass
from typing import Optional

from guardian_management_api.models.base import (
    NamespacedResponseObject,
    PaginationRequest,
)


class ResponseRole(NamespacedResponseObject):
    app_name: str
    name: str


@dataclass(frozen=True)
class Role:
    app_name: str
    namespace_name: str
    name: str
    display_name: Optional[str] = None


@dataclass(frozen=True)
class RoleGetQuery:
    app_name: str
    namespace_name: str
    name: str


@dataclass(frozen=True)
class RolesGetQuery:
    pagination: PaginationRequest
