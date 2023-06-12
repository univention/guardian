from dataclasses import dataclass, field
from typing import Any, Iterable, Optional

from guardian_authorization_api.models.settings import SETTINGS_NAME_METADATA

OPA_URL_SETTING_NAME = "opa_adapter.url"


@dataclass
class OPAAdapterSettings:
    opa_url: str = field(metadata={SETTINGS_NAME_METADATA: OPA_URL_SETTING_NAME})


@dataclass(frozen=True)
class NamespacedValue:
    app_name: str
    namespace_name: str
    name: str


@dataclass(frozen=True)
class Role(NamespacedValue):
    ...


@dataclass(frozen=True)
class Permission(NamespacedValue):
    ...


@dataclass(frozen=True)
class Context(NamespacedValue):
    ...


@dataclass(frozen=True)
class Policy(NamespacedValue):
    """
    This dataclass represents a custom policy that was registered in the Guardian Management API.
    """

    ...


@dataclass(frozen=True)
class Namespace:
    app_name: str
    name: str


@dataclass(frozen=True)
class PolicyObject:
    """Actor or target sent to the policy agent to evaluate permissions"""

    id: str
    roles: list["Role"]
    attributes: dict[str, Any]


@dataclass(frozen=True)
class Target:
    old_target: Optional[PolicyObject]
    new_target: Optional[PolicyObject]


@dataclass(frozen=True)
class CheckResult:
    target_id: str
    actor_has_permissions: bool


@dataclass(frozen=True)
class TargetPermissions:
    target_id: str
    permissions: Iterable[Permission]


@dataclass(frozen=True)
class CheckPermissionsResult:
    target_permissions: Iterable[CheckResult]
    actor_has_general_permissions: Optional[bool]


@dataclass(frozen=True)
class GetPermissionsResult:
    target_permissions: Iterable[TargetPermissions]
    general_permissions: Optional[Iterable[Permission]] = None
