# Copyright (C) 2023 Univention GmbH
#
# SPDX-License-Identifier: AGPL-3.0-only

from pydantic import BaseModel, Field

from guardian_management_api.models.condition import ConditionParameterType
from guardian_management_api.models.routers.base import (
    CreateBaseRequest,
    DisplayNameObjectMixin,
    DocumentationObjectMixin,
    EditBaseRequest,
    GuardianBaseModel,
    ManagementObjectName,
    NameObjectMixin,
    NamespacedObjectMixin,
    PaginationObjectMixin,
    RawCodeObjectMixin,
    ResourceURLObjectMixin,
)

#####
# Requests
#####


# Type alias for condition parameter names (same constraints as ManagementObjectName)
ConditionParameterName = ManagementObjectName


class ConditionParameter(GuardianBaseModel):
    name: ConditionParameterName
    value_type: ConditionParameterType = ConditionParameterType.ANY


class ConditionParametersMixin(BaseModel):
    parameters: list[ConditionParameter] = Field(
        [],
        description="The list of parameters the condition expects. "
        "This is informational only and not validated during the creation of capabilities.",
    )


class ConditionCreateData(
    GuardianBaseModel,
    RawCodeObjectMixin,
    ConditionParametersMixin,
    DocumentationObjectMixin,
    DisplayNameObjectMixin,
    NameObjectMixin,
): ...


class ConditionCreateRequest(CreateBaseRequest):
    data: ConditionCreateData


class ConditionEditData(
    GuardianBaseModel,
    RawCodeObjectMixin,
    ConditionParametersMixin,
    DocumentationObjectMixin,
    DisplayNameObjectMixin,
): ...


class ConditionEditRequest(EditBaseRequest):
    data: ConditionEditData


#####
# Responses
#####


class Condition(
    GuardianBaseModel,
    ConditionParametersMixin,
    DocumentationObjectMixin,
    ResourceURLObjectMixin,
    DisplayNameObjectMixin,
    NamespacedObjectMixin,
): ...


class ConditionSingleResponse(GuardianBaseModel):
    condition: Condition


class ConditionMultipleResponse(GuardianBaseModel, PaginationObjectMixin):
    conditions: list[Condition]
