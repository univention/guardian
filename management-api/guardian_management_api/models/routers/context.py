# Copyright (C) 2023 Univention GmbH
#
# SPDX-License-Identifier: AGPL-3.0-only

from guardian_management_api.models.routers.base import (
    AppNamePathMixin,
    AppScopedCreateBaseRequest,
    AppScopedEditBaseRequest,
    AppScopedObjectMixin,
    DisplayNameObjectMixin,
    GuardianBaseModel,
    NameObjectMixin,
    NamePathMixin,
    PaginationObjectMixin,
    PaginationRequestMixin,
    ResourceURLObjectMixin,
)

#####
# Requests
#####


class ContextCreateData(GuardianBaseModel, DisplayNameObjectMixin, NameObjectMixin): ...


class ContextCreateRequest(AppScopedCreateBaseRequest):
    data: ContextCreateData


class ContextEditData(GuardianBaseModel, DisplayNameObjectMixin): ...


class ContextEditRequest(AppScopedEditBaseRequest):
    data: ContextEditData


class ContextGetRequest(GuardianBaseModel, NamePathMixin, AppNamePathMixin): ...


class ContextsGetRequest(GuardianBaseModel, PaginationRequestMixin): ...


class ContextsByAppnameGetRequest(GuardianBaseModel, PaginationRequestMixin):
    app_name: str


#####
# Responses
#####


class Context(
    GuardianBaseModel,
    ResourceURLObjectMixin,
    DisplayNameObjectMixin,
    AppScopedObjectMixin,
): ...


class ContextSingleResponse(GuardianBaseModel):
    context: Context


class ContextMultipleResponse(GuardianBaseModel, PaginationObjectMixin):
    contexts: list[Context]
