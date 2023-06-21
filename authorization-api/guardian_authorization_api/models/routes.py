from typing import Any, Optional

from pydantic import BaseModel, ConstrainedStr, Field


class GuardianBaseModel(BaseModel):
    class Config:
        allow_population_by_field_name = True


class ObjectIdentifier(ConstrainedStr):
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
    name: ObjectIdentifier


class Object(GuardianBaseModel):
    id: ObjectIdentifier
    roles: list[Role]
    attributes: dict[str, Any]


class Actor(Object):
    """Representation of an actor. An actor must contain a roles attribute."""


class Permission(GuardianBaseModel):
    app_name: AppName
    namespace_name: NamespaceName
    name: PermissionName


class Target(GuardianBaseModel):
    """A target has a current state and an updated state and field which identify the object"""

    old_target: Optional[Object]
    new_target: Optional[Object]


class Context(GuardianBaseModel):
    app_name: AppName
    namespace_name: NamespaceName
    name: ContextName
    displayname: ContextDisplayName


class AuthzPermissionsPostRequest(GuardianBaseModel):
    namespaces: Optional[list[NamespaceMinimal]] = Field(default=None)
    actor: Actor
    targets: Optional[list[Target]]
    contexts: Optional[list[Context]]
    include_general_permissions: bool = False
    extra_request_data: dict[str, Any]


class PermissionResult(GuardianBaseModel):
    """
    Represents the answer to the question:
    What permissions are available for 'actor' with respect to 'target'
    """

    target_id: ObjectIdentifier
    permissions: list[Permission]


class AuthzPermissionsPostResponse(GuardianBaseModel):
    actor_id: ObjectIdentifier
    general_permissions: list[Permission]
    target_permissions: list[PermissionResult]
