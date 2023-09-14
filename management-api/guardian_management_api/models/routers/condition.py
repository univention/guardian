# Copyright (C) 2023 Univention GmbH
#
# SPDX-License-Identifier: AGPL-3.0-only

from pydantic import BaseModel, ConstrainedStr, Field

from guardian_management_api.constants import STRING_MAX_LENGTH
from guardian_management_api.models.condition import ConditionParameterType
from guardian_management_api.models.routers.base import (
    CreateBaseRequest,
    DisplayNameObjectMixin,
    DocumentationObjectMixin,
    EditBaseRequest,
    GuardianBaseModel,
    NameObjectMixin,
    NamespacedObjectMixin,
    PaginationObjectMixin,
    RawCodeObjectMixin,
    ResourceURLObjectMixin,
)

#####
# Requests
#####


class ConditionParameterName(ConstrainedStr):
    """Name of a conditions parameter"""

    regex = r"[a-z][a-z0-9_]*"
    min_length = 1
    max_length = STRING_MAX_LENGTH


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
):
    ...


class ConditionCreateRequest(CreateBaseRequest):
    data: ConditionCreateData


class ConditionEditData(
    GuardianBaseModel,
    RawCodeObjectMixin,
    ConditionParametersMixin,
    DocumentationObjectMixin,
    DisplayNameObjectMixin,
):
    ...


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
):
    ...


class ConditionSingleResponse(GuardianBaseModel):
    condition: Condition


class ConditionMultipleResponse(GuardianBaseModel, PaginationObjectMixin):
    conditions: list[Condition]
