# Copyright (C) 2023 Univention GmbH
#
# SPDX-License-Identifier: AGPL-3.0-only

from enum import StrEnum
from typing import Any, Optional

from pydantic import Field, root_validator

from guardian_management_api.models.condition import ConditionParameterType
from guardian_management_api.models.routers.base import (
    AppNamePathMixin,
    CreateBaseRequest,
    DisplayNameObjectMixin,
    EditBaseRequest,
    GuardianBaseModel,
    ManagementObjectName,
    NamePathMixin,
    NamespacedObjectMixin,
    NamespacePathMixin,
    PaginationObjectMixin,
    PaginationRequestMixin,
    ResourceURLObjectMixin,
)
from guardian_management_api.models.routers.condition import ConditionParameterName


def check_permissions_in_namespace(cls, values: dict[str, Any]):
    """
    This function validates that a given permission is in the namespace of its parent capability.

    This validator is intended to be used as a root validator on the Create and Edit Request objects.
    """
    namespace = f"{values.get('app_name', '')}:{values.get('namespace_name', '')}"
    permissions: list[CapabilityPermission] = values["data"].permissions
    for permission in permissions:
        permission_namespace = f"{permission.app_name}:{permission.namespace_name}"
        if permission_namespace != namespace:
            raise ValueError(
                "The request contains permissions, which are in a different namespace than the "
                "capability itself."
            )
    return values


#####
# Requests
#####


class CapabilityRole(GuardianBaseModel, NamespacedObjectMixin):
    ...


class CapabilityPermission(GuardianBaseModel, NamespacedObjectMixin):
    ...


class CapabilityConditionParameter(GuardianBaseModel):
    name: ConditionParameterName
    value: Any
    value_type: ConditionParameterType


class CapabilityCondition(GuardianBaseModel, NamespacedObjectMixin):
    parameters: list[CapabilityConditionParameter] = Field(
        ..., description="The preset parameter values for the condition."
    )


class CapabilityEditConditionParameter(GuardianBaseModel):
    name: ConditionParameterName
    value: Any


class CapabilityEditCondition(GuardianBaseModel, NamespacedObjectMixin):
    parameters: list[CapabilityEditConditionParameter] = Field(
        ..., description="The preset parameter values for the condition."
    )


class RelationChoices(StrEnum):
    AND = "AND"
    OR = "OR"


class CapabilityCreateData(GuardianBaseModel, DisplayNameObjectMixin):
    name: Optional[ManagementObjectName] = Field(
        None,
        description="The name of the new capability. If no name is provided, one is generated",
    )
    role: CapabilityRole = Field(
        ..., description="The role this capability attaches to."
    )
    conditions: list[CapabilityEditCondition] = Field(
        ..., description="The list of conditions that apply to this capability."
    )
    relation: RelationChoices = Field(
        ..., description="The relation that is applied to the conditions."
    )
    permissions: list[CapabilityPermission] = Field(
        ..., description="The list of permissions this capability grants to the role."
    )


class CapabilityEditData(GuardianBaseModel, DisplayNameObjectMixin):
    role: CapabilityRole = Field(
        ..., description="The role this capability attaches to."
    )
    conditions: list[CapabilityEditCondition] = Field(
        ..., description="The list of conditions that apply to this capability."
    )
    relation: RelationChoices = Field(
        ..., description="The relation that is applied to the conditions."
    )
    permissions: list[CapabilityPermission] = Field(
        ..., description="The list of permissions this capability grants to the role."
    )


class CapabilityCreateRequest(CreateBaseRequest):
    data: CapabilityCreateData

    _check_permissions_in_namespace = root_validator(allow_reuse=True, pre=True)(
        check_permissions_in_namespace
    )


class CapabilityEditRequest(EditBaseRequest):
    data: CapabilityEditData

    _check_permissions_in_namespace = root_validator(allow_reuse=True, pre=True)(
        check_permissions_in_namespace
    )


class CapabilitiesGetByRoleRequest(
    GuardianBaseModel,
    NamePathMixin,
    NamespacePathMixin,
    AppNamePathMixin,
    PaginationRequestMixin,
):
    ...


#####
# Responses
#####


class Capability(
    GuardianBaseModel,
    ResourceURLObjectMixin,
    DisplayNameObjectMixin,
    NamespacedObjectMixin,
):
    role: CapabilityRole = Field(
        ..., description="The role this capability attaches to."
    )
    conditions: list[CapabilityCondition] = Field(
        ..., description="The list of conditions that apply to this capability."
    )
    relation: RelationChoices = Field(
        ..., description="The relation that is applied to the conditions."
    )
    permissions: list[CapabilityPermission] = Field(
        ..., description="The list of permissions this capability grants to the role."
    )


class CapabilitySingleResponse(GuardianBaseModel):
    capability: Capability


class CapabilityMultipleResponse(GuardianBaseModel, PaginationObjectMixin):
    capabilities: list[Capability]
