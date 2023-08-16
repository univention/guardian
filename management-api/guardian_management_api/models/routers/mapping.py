# Copyright (C) 2023 Univention GmbH
#
# SPDX-License-Identifier: AGPL-3.0-only
from enum import StrEnum

from pydantic import Field

from guardian_management_api.models.routers.base import (
    AppNamePathMixin,
    CreateBaseRequest,
    GuardianBaseModel,
    NamespacedObjectMixin,
    NamespacePathMixin,
)


class MappingRole(GuardianBaseModel, NamespacedObjectMixin):
    ...


class MappingCondition(GuardianBaseModel, NamespacedObjectMixin):
    parameters: dict[str, str | bool | int | float] = Field(
        ..., description="The preset parameter values for the condition."
    )


class MappingPermission(GuardianBaseModel, NamespacedObjectMixin):
    ...


class RelationChoices(StrEnum):
    AND = "AND"
    OR = "OR"


class Capability(GuardianBaseModel):
    role: MappingRole = Field(..., description="The role this capability belongs to.")
    conditions: list[MappingCondition] = Field(
        ...,
        description="The list of conditions that determine if this capability applies.",
    )
    relation: RelationChoices = Field(
        ..., description="The type of relation to evaluate the conditions with."
    )
    permissions: list[MappingPermission] = Field(
        ..., description="The list of permissions that the capability is granting."
    )


class RCMapping(GuardianBaseModel):
    mappings: list[Capability] = Field(
        ..., description="The list of capabilities mapped to roles."
    )


#####
# Requests
#####


class RCMappingGetAllRequest(GuardianBaseModel):
    ...


class RCMappingGetByNamespaceRequest(
    GuardianBaseModel, NamespacePathMixin, AppNamePathMixin
):
    ...


class RCMappingUpdateByNamespaceRequest(CreateBaseRequest):
    data: RCMapping


class RCMappingUpdateAllRequest(GuardianBaseModel):
    data: RCMapping


class RCMappingDeleteRequest(GuardianBaseModel, NamespacePathMixin, AppNamePathMixin):
    ...


#####
# Responses
#####


class RCMappingResponse(GuardianBaseModel):
    role_capability_mapping: RCMapping
