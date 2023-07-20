# Copyright (C) 2023 Univention GmbH
#
# SPDX-License-Identifier: AGPL-3.0-only

from typing import Any, Optional

from pydantic import BaseModel, ConstrainedStr, Field


class GuardianBaseModel(BaseModel):
    class Config:
        allow_population_by_field_name = True


class AuthzObjectIdentifier(ConstrainedStr):
    """Identifies an object in an authz check"""

    __root__: str = Field(example="6f8be20a-d463-454d-8ccf-bf6227437473", min_length=3)


class AppName(ConstrainedStr):
    """Name of an application"""

    __root__: str = Field(
        example="ucsschool-kelvin-rest-api", regex=r"[a-z][a-z0-9\-]*", min_length=3
    )


class NamespaceName(ConstrainedStr):
    """Name of a namespace"""

    __root__: str = Field(
        example="kelvin-rest-api", regex=r"[a-z][a-z0-9\-]*", min_length=3
    )


class ContextName(ConstrainedStr):
    __root__: str = Field(example="school_a", min_length=3)


class ContextDisplayName(ConstrainedStr):
    __root__: str = Field(example="School A", min_length=3)


class PermissionName(ConstrainedStr):
    __root__: str = Field(example="reset_password", min_length=3)


class NamespaceMinimal(GuardianBaseModel):
    """A minimal namespace object for requests (e.g. role-capability-mapping)"""

    app_name: AppName
    name: NamespaceName


class Role(GuardianBaseModel):
    app_name: AppName
    namespace_name: NamespaceName
    name: AuthzObjectIdentifier


class AuthzObject(GuardianBaseModel):
    id: AuthzObjectIdentifier
    roles: list[Role]
    attributes: dict[str, Any]


class AuthzObjectLookup(GuardianBaseModel):
    id: AuthzObjectIdentifier


class Actor(AuthzObject):
    """Representation of an actor. An actor must contain a roles attribute."""


class ActorLookup(AuthzObjectLookup):
    """Representation of an actor that needs to be looked up in the data store."""


class Permission(GuardianBaseModel):
    app_name: AppName
    namespace_name: NamespaceName
    name: PermissionName


class Target(GuardianBaseModel):
    """A target has a current state and an updated state and field which identify the object"""

    old_target: Optional[AuthzObject]
    new_target: Optional[AuthzObject]


class TargetLookup(GuardianBaseModel):
    """
    Representation of a target that needs to be looked up in the data store.
    A lookup target may have a current state and updated state.
    """

    old_target: Optional[AuthzObjectLookup]
    new_target: Optional[AuthzObject]


class Context(GuardianBaseModel):
    app_name: AppName
    namespace_name: NamespaceName
    name: ContextName
    display_name: ContextDisplayName


class AuthzPermissionsPostRequest(GuardianBaseModel):
    namespaces: Optional[list[NamespaceMinimal]] = Field(default=None)
    actor: Actor
    targets: Optional[list[Target]]
    contexts: Optional[list[Context]]
    include_general_permissions: bool = False
    extra_request_data: dict[str, Any]


class AuthzPermissionsLookupPostRequest(GuardianBaseModel):
    namespaces: Optional[list[NamespaceMinimal]] = Field(default=None)
    actor: ActorLookup
    targets: Optional[list[TargetLookup]]
    contexts: Optional[list[Context]]
    include_general_permissions: bool = False
    extra_request_data: dict[str, Any]


class AuthzPermissionsCheckPostRequest(GuardianBaseModel):
    namespaces: Optional[list[NamespaceMinimal]] = Field(default=None)
    actor: Actor
    targets: Optional[list[Target]]
    contexts: Optional[list[Context]]
    permissions_to_check: list[Permission]
    extra_request_data: dict[str, Any]


class AuthzPermissionsCheckLookupPostRequest(GuardianBaseModel):
    namespaces: Optional[list[NamespaceMinimal]] = Field(default=None)
    actor: ActorLookup
    targets: Optional[list[TargetLookup]]
    contexts: Optional[list[Context]]
    permissions_to_check: list[Permission]
    extra_request_data: dict[str, Any]


class AuthzCustomEndpointPostRequest(GuardianBaseModel):
    pass


class PermissionResult(GuardianBaseModel):
    """
    Represents the answer to the question:
    What permissions are available for 'actor' with respect to 'target'?
    """

    target_id: AuthzObjectIdentifier
    permissions: list[Permission]


class PermissionCheckResult(GuardianBaseModel):
    """
    Represents the answer to the question:
    Does the 'actor' have all permissions with respect to the 'target'?
    """

    target_id: AuthzObjectIdentifier
    actor_has_permissions: bool


class AuthzPermissionsPostResponse(GuardianBaseModel):
    actor_id: AuthzObjectIdentifier
    general_permissions: list[Permission]
    target_permissions: list[PermissionResult]


class AuthzPermissionsCheckPostResponse(GuardianBaseModel):
    actor_id: AuthzObjectIdentifier
    permissions_check_results: list[PermissionCheckResult]
    actor_has_all_permissions: bool


class AuthzCustomEndpointPostResponse(GuardianBaseModel):
    pass
