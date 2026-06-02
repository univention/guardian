# Copyright (C) 2023 Univention GmbH
#
# SPDX-License-Identifier: AGPL-3.0-only

from typing import Optional

from pydantic import Field

from guardian_management_api.models.capability import CapabilityReference
from guardian_management_api.models.routers.base import (
    AppScopedCreateBaseRequest,
    AppScopedEditBaseRequest,
    AppScopedObjectMixin,
    DisplayNameObjectMixin,
    GetAllRequest,
    GetByAppFullIdentifierRequest,
    GetByAppRequest,
    GuardianBaseModel,
    NameObjectMixin,
    NamespacedObjectMixin,
    PaginationObjectMixin,
    ResourceURLObjectMixin,
)


class RoleCapability(GuardianBaseModel, NamespacedObjectMixin):
    """Reference to a capability from a role (identifier only)."""

    def to_reference(self) -> CapabilityReference:
        return CapabilityReference(
            app_name=self.app_name,
            namespace_name=self.namespace_name,
            name=self.name,
        )


#####
# Requests
#####


# request for route: GET .../roles/{app_name}/{name}
class RoleGetFullIdentifierRequest(GetByAppFullIdentifierRequest): ...


class RoleCreateData(GuardianBaseModel, DisplayNameObjectMixin, NameObjectMixin):
    capabilities: list[RoleCapability] = Field(
        default_factory=list,
        description="The list of capabilities assigned to this role.",
    )


# request for route: POST .../roles/{app_name}
class RoleCreateRequest(AppScopedCreateBaseRequest):
    data: RoleCreateData


class RoleEditData(GuardianBaseModel, DisplayNameObjectMixin):
    capabilities: Optional[list[RoleCapability]] = Field(
        default=None,
        description=(
            "The list of capabilities assigned to this role. "
            "Omit or set to null to leave the assignment unchanged; "
            "set to an empty list to remove all capabilities."
        ),
    )


# request for route: PATCH .../roles/{app_name}/{name}
class RoleEditRequest(AppScopedEditBaseRequest):
    data: RoleEditData


# request for route: GET .../roles
class RoleGetAllRequest(GetAllRequest): ...


# request for route: GET .../roles/{app_name}
class RoleGetByAppRequest(GetByAppRequest): ...


#####
# Responses
#####


class Role(
    GuardianBaseModel,
    ResourceURLObjectMixin,
    DisplayNameObjectMixin,
    AppScopedObjectMixin,
):
    capabilities: list[RoleCapability] = Field(
        default_factory=list,
        description="The list of capabilities assigned to this role.",
    )


class RoleSingleResponse(GuardianBaseModel):
    role: Role


class RoleMultipleResponse(GuardianBaseModel, PaginationObjectMixin):
    roles: list[Role]
