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
