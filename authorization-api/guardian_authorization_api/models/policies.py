# Copyright (C) 2023 Univention GmbH
#
# SPDX-License-Identifier: AGPL-3.0-only

from dataclasses import dataclass, field
from typing import Any, Optional

from guardian_lib.models.settings import SETTINGS_NAME_METADATA

OPA_URL_SETTING_NAME = "opa_adapter.url"


@dataclass
class OPAAdapterSettings:
    opa_url: str = field(metadata={SETTINGS_NAME_METADATA: OPA_URL_SETTING_NAME})


@dataclass(frozen=True)
class NamespacedValue:
    app_name: str
    namespace_name: str
    name: str

    def __str__(self):
        return f"{self.app_name}:{self.namespace_name}:{self.name}"


@dataclass(frozen=True)
class Permission(NamespacedValue):
    ...


@dataclass(frozen=True)
class Context(NamespacedValue):
    ...


@dataclass(frozen=True)
class Role(NamespacedValue):
    context: Optional[Context] = None

    def __str__(self):
        if self.context:
            return f"{super().__str__()}&{self.context}"
        else:
            return f"{super().__str__()}"


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
    roles: list[Role]
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
    permissions: list[Permission]


@dataclass(frozen=True)
class CheckPermissionsResult:
    target_permissions: list[CheckResult]
    actor_has_general_permissions: Optional[bool]


@dataclass(frozen=True)
class GetPermissionsResult:
    actor: PolicyObject
    target_permissions: list[TargetPermissions]
    general_permissions: Optional[list[Permission]] = None


@dataclass(frozen=True)
class GetPermissionsQuery:
    actor: PolicyObject
    targets: Optional[list[Target]] = None
    namespaces: Optional[list[Namespace]] = None
    contexts: Optional[list[Context]] = None
    extra_args: Optional[dict[str, Any]] = None
    include_general_permissions: bool = False


@dataclass(frozen=True)
class CheckPermissionsQuery:
    actor: PolicyObject
    targets: Optional[list[Target]] = None
    namespaces: Optional[list[Namespace]] = None
    target_permissions: Optional[list[Permission]] = None
    general_permissions: Optional[list[Permission]] = None
    contexts: Optional[list[Context]] = None
    extra_args: Optional[dict[str, Any]] = None
