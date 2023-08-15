# Copyright (C) 2023 Univention GmbH
#
# SPDX-License-Identifier: AGPL-3.0-only

from guardian_management_api.models.routers.base import (
    CreateBaseRequest,
    DisplayNameObjectMixin,
    EditBaseRequest,
    GuardianBaseModel,
    NameObjectMixin,
    NamespacedObjectMixin,
    PaginationObjectMixin,
    ResourceURLObjectMixin,
)

#####
# Requests
#####


class ContextCreateData(GuardianBaseModel, DisplayNameObjectMixin, NameObjectMixin):
    ...


class ContextCreateRequest(CreateBaseRequest):
    data: ContextCreateData


class ContextEditData(GuardianBaseModel, DisplayNameObjectMixin):
    ...


class ContextEditRequest(EditBaseRequest):
    data: ContextEditData


#####
# Responses
#####


class Context(
    GuardianBaseModel,
    ResourceURLObjectMixin,
    DisplayNameObjectMixin,
    NamespacedObjectMixin,
):
    ...


class ContextSingleResponse(GuardianBaseModel):
    context: Context


class ContextMultipleResponse(GuardianBaseModel, PaginationObjectMixin):
    contexts: list[Context]
