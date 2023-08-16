# Copyright (C) 2023 Univention GmbH
#
# SPDX-License-Identifier: AGPL-3.0-only
from pydantic import BaseModel, Field

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


class ConditionParameterNamesMixin(BaseModel):
    parameter_names: list[str] = Field(
        [], description="The list of parameters the condition expects."
    )


class ConditionCreateData(
    GuardianBaseModel,
    RawCodeObjectMixin,
    ConditionParameterNamesMixin,
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
    ConditionParameterNamesMixin,
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
    ConditionParameterNamesMixin,
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
