"""
This file contains proposals for the ports in the authz API.
It should be deleted once the actual implementations exist
"""

from abc import ABC
from dataclasses import dataclass
from enum import Enum
from typing import Any, Iterable, Optional, Type

# Models


class ObjectType(Enum):
    USER = 0
    GROUP = 1
    UNKNOWN = 2


@dataclass
class PolicyObject:
    """Actor or target sent to the policy agent to evaluate permissions"""

    id: str
    roles: set["Role"]
    attributes: dict[str, Any]


@dataclass
class Target:
    old_target: Optional[PolicyObject]
    new_target: Optional[PolicyObject]


@dataclass
class PersistenceObject:
    """
    Actor or target retrieved from data storage.
    The ``object_type`` is a hint to the PersistancePort on how to
    construct the query to the data store, such as hinting which
    table to use or how to construct the dn.
    """

    id: str
    object_type: ObjectType
    attributes: dict[str, Any]


@dataclass
class NamespacedValue:
    app_name: str
    namespace_name: str
    name: str


@dataclass
class Context(NamespacedValue):
    ...


@dataclass
class Permission(NamespacedValue):
    ...


class Role(NamespacedValue):
    ...


class Policy(NamespacedValue):
    ...


@dataclass
class RequestRole(NamespacedValue):
    ...


@dataclass
class RequestActor:
    id: str
    roles: Iterable[RequestRole]
    attributes: dict[str, Any]


@dataclass
class RequestTarget:
    id: str
    roles: Iterable[RequestRole]
    current_attributes: dict[str, Any]
    updated_attributes: dict[str, Any]


@dataclass
class RequestContext(NamespacedValue):
    ...


@dataclass
class RequestPermission(NamespacedValue):
    ...


@dataclass
class RequestNamespace:
    app_name: str
    name: str


@dataclass
class PermissionCheckResult:
    target_id: str
    actor_has_permissions: bool


@dataclass
class CheckPermissionAPIResponse:
    target_permission_check_results: Iterable[PermissionCheckResult]
    actor_has_all_target_permissions: bool
    actor_has_all_general_permissions: bool


@dataclass
class GetPermissionAPIResult:
    target_id: str
    permissions: Iterable[RequestPermission]


class GetPermissionAPIResponse:
    target_permissions: Iterable[GetPermissionAPIResult]
    general_permissions: Optional[Iterable[RequestPermission]]


@dataclass
class CheckPermissionResult:
    target_id: str
    actor_has_permissions: bool


@dataclass
class GetPermissionsResult:
    target_id: str
    permissions: Iterable[Permission]


@dataclass
class GetPermissionsResponse:
    target_permissions: Iterable[GetPermissionsResult]
    general_permissions: Optional[Iterable[Permission]]


@dataclass
class CheckPermissionsResponse:
    target_permissions: Iterable[CheckPermissionResult]
    actor_has_general_permissions: bool


# Incoming Ports


class CheckPermissionAPIPort(ABC):
    async def check_permissions(
        self,
        actor: RequestActor,
        targets: Iterable[RequestTarget],
        contexts: Iterable[RequestContext],
        target_permissions: Iterable[RequestPermission],
        general_permissions: Iterable[RequestPermission],
        extra_request_data: dict[str, Any],
    ) -> CheckPermissionAPIResponse:
        raise NotImplementedError


class GetPermissionAPIPort(ABC):
    async def get_permissions(
        self,
        actor: RequestActor,
        targets: Iterable[RequestTarget],
        contexts: Iterable[RequestContext],
        extra_request_data: dict[str, Any],
        namespaces: Iterable[RequestNamespace],
        include_general_permissions: bool,
    ) -> GetPermissionAPIResponse:  # but validated
        raise NotImplementedError


class CustomPolicyPort(ABC):
    async def custom_policy(self, policy: Policy, data: dict[str, Any]) -> Any:
        raise NotImplementedError


# Outgoing Ports


class SettingsPort(ABC):
    # The Adapter should ideally be lazy-loaded,
    # even when implementing the Mapping Protocol
    # The Adapter should ideally be cached as well

    async def get_setting(
        self, setting_name: str, setting_type: Type, default: Any = None
    ) -> Any:
        raise NotImplementedError


class PolicyPort(ABC):
    async def check_permissions(
        self,
        actor: PolicyObject,
        targets: Iterable[Target],
        target_permissions: set[Permission],
        general_permissions: set[Permission],
        context: set[Context],
        extra_args: dict[str, Any],
    ) -> CheckPermissionsResponse:
        raise NotImplementedError

    async def get_permissions(
        self,
        actor: PolicyObject,
        targets: Iterable[Target],
        contexts: Iterable[Context],
        extra_args: dict[str, Any],
        include_general_permissions: bool,
    ) -> GetPermissionsResponse:
        raise NotImplementedError

    async def custom_policy(
        self, policy: Policy, data: dict[str, Any]
    ) -> dict[str, Any]:
        raise NotImplementedError


class PersistencePort(ABC):
    async def get_object(
        self, identifier: str, object_type: ObjectType
    ) -> PersistenceObject:
        raise NotImplementedError
