from typing import Any, Optional

from pydantic import BaseModel, ConstrainedStr, Field

from .incoming import GetPermissionAPIResponse
from .policies import PolicyObject
from .policies import Role as PoliciesRole
from .policies import Target as PoliciesTarget


class GuardianBaseModel(BaseModel):
    class Config:
        allow_population_by_field_name = True


class ObjectIdentifier(ConstrainedStr):
    """Identifies an object in an authz check"""

    __root__: str = Field(example="6f8be20a-d463-454d-8ccf-bf6227437473", min_length=1)


class AppName(ConstrainedStr):
    """Name of an application"""

    __root__: str = Field(
        example="ucsschool-kelvin-rest-api", regex=r"[a-z][a-z0-9\-]*", min_length=1
    )


class NamespaceName(ConstrainedStr):
    """Name of a namespace"""

    __root__: str = Field(
        example="kelvin-rest-api", regex=r"[a-z][a-z0-9\-]*", min_length=1
    )


class ContextName(ConstrainedStr):
    __root__: str = Field(example="school_a")


class ContextDisplayName(ConstrainedStr):
    __root__: str = Field(example="School A")


class PermissionName(ConstrainedStr):
    __root__: str = Field(example="reset_password")


class NamespaceMinimal(GuardianBaseModel):
    """A minimal namespace object for requests (e.g. role-capability-mapping)"""

    app_name: AppName
    namespace_name: NamespaceName


class Role(GuardianBaseModel):
    app_name: AppName
    namespace_name: NamespaceName
    role_name: PermissionName


class Object(GuardianBaseModel):
    id: ObjectIdentifier
    roles: list[Role]
    attributes: dict[str, Any]

    def to_policy_object(
        self,
    ) -> PolicyObject:
        return PolicyObject(
            id=str(self.id),
            roles=[
                PoliciesRole(
                    app_name=role.app_name,
                    namespace_name=role.app_name,
                    name=role.role_name,
                )
                for role in self.roles
            ],
            attributes=self.attributes,
        )


class Actor(Object):
    """Representation of an actor. An actor must contain a roles attribute."""


class Permission(GuardianBaseModel):
    app_name: AppName
    namespace_name: NamespaceName
    permission_name: PermissionName


class Target(GuardianBaseModel):
    """A target has a current state and an updated state and field which identify the object"""

    old_target: Object
    new_target: Object

    def to_policies_target(self) -> PoliciesTarget:
        return PoliciesTarget(
            old_target=self.old_target.to_policy_object(),
            new_target=self.new_target.to_policy_object(),
        )


class Context(GuardianBaseModel):
    app_name: AppName
    namespace_name: NamespaceName
    context_name: ContextName
    context_displayname: ContextDisplayName


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

    @classmethod
    def from_get_permissions_api_response(
        cls, actor_id: str, api_response: GetPermissionAPIResponse
    ):
        target_permissions = [
            PermissionResult(
                target_id=target_p.target_id,
                permissions=[
                    Permission(
                        permission_name=perm.name,
                        namespace_name=perm.namespace_name,
                        app_name=perm.app_name,
                    )
                    for perm in target_p.permissions
                ],
            )
            for target_p in api_response.target_permissions
        ]
        general_permissions = (
            [
                Permission(
                    app_name=perm.app_name,
                    namespace_name=perm.namespace_name,
                    permission_name=perm.name,
                )
                for perm in api_response.general_permissions
            ]
            if api_response.general_permissions
            else []
        )
        return cls(
            actor_id=actor_id,
            target_permissions=target_permissions,
            general_permissions=general_permissions,
        )
