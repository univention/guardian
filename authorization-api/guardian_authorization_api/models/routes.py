# Copyright (C) 2023 Univention GmbH
#
# SPDX-License-Identifier: AGPL-3.0-only

from typing import Annotated, Any, Optional

from pydantic import BaseModel, ConfigDict, Field, StringConstraints


class GuardianBaseModel(BaseModel):
    model_config = ConfigDict(populate_by_name=True)


AuthzObjectIdentifier = Annotated[str, StringConstraints(min_length=3)]


AppName = Annotated[str, StringConstraints(pattern=r"^[a-z][a-z0-9\-]*$", min_length=3)]


NamespaceName = Annotated[
    str, StringConstraints(pattern=r"^[a-z][a-z0-9\-]*$", min_length=3)
]


ContextName = Annotated[str, StringConstraints(min_length=3)]


ContextDisplayName = Annotated[str, StringConstraints(min_length=3)]


PermissionName = Annotated[str, StringConstraints(min_length=3)]


class NamespaceMinimal(GuardianBaseModel):
    """A minimal namespace object for requests (e.g. role-capability-mapping)"""

    app_name: AppName
    name: NamespaceName


class Context(GuardianBaseModel):
    app_name: AppName
    namespace_name: NamespaceName
    name: ContextName


class Role(GuardianBaseModel):
    app_name: AppName
    namespace_name: NamespaceName
    name: AuthzObjectIdentifier
    context: Optional[Context] = None


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


class AuthzPermissionsPostRequest(GuardianBaseModel):
    namespaces: Optional[list[NamespaceMinimal]] = Field(default=None)
    actor: Actor
    targets: Optional[list[Target]] = None
    contexts: Optional[list[Context]] = None
    include_general_permissions: bool = False
    extra_request_data: dict[str, Any]


class AuthzPermissionsLookupPostRequest(GuardianBaseModel):
    namespaces: Optional[list[NamespaceMinimal]] = Field(default=None)
    actor: ActorLookup
    targets: Optional[list[Target | TargetLookup]] = None
    contexts: Optional[list[Context]] = None
    include_general_permissions: bool = False
    extra_request_data: dict[str, Any]


class AuthzPermissionsCheckPostRequest(GuardianBaseModel):
    namespaces: Optional[list[NamespaceMinimal]] = Field(default=None)
    actor: Actor
    targets: Optional[list[Target]] = None
    contexts: Optional[list[Context]] = None
    targeted_permissions_to_check: list[Permission]
    general_permissions_to_check: list[Permission]
    extra_request_data: dict[str, Any]


class AuthzPermissionsCheckLookupPostRequest(GuardianBaseModel):
    namespaces: Optional[list[NamespaceMinimal]] = Field(default=None)
    actor: ActorLookup
    targets: Optional[list[Target | TargetLookup]] = None
    contexts: Optional[list[Context]] = None
    targeted_permissions_to_check: list[Permission]
    general_permissions_to_check: list[Permission]
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
    actor_has_all_general_permissions: bool
    actor_has_all_targeted_permissions: bool


class AuthzCustomEndpointPostResponse(GuardianBaseModel):
    pass
