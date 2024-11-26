# Copyright (C) 2023 Univention GmbH
#
# SPDX-License-Identifier: AGPL-3.0-only

from guardian_management_api.models.routers.base import (
    AppNamePathMixin,
    CreateBaseRequest,
    DisplayNameObjectMixin,
    EditBaseRequest,
    GuardianBaseModel,
    NameObjectMixin,
    NamePathMixin,
    NamespacedObjectMixin,
    NamespacePathMixin,
    PaginationObjectMixin,
    PaginationRequestMixin,
    ResourceURLObjectMixin,
)

#####
# Requests
#####


class ContextCreateData(GuardianBaseModel, DisplayNameObjectMixin, NameObjectMixin): ...


class ContextCreateRequest(CreateBaseRequest):
    data: ContextCreateData


class ContextEditData(GuardianBaseModel, DisplayNameObjectMixin): ...


class ContextEditRequest(EditBaseRequest):
    data: ContextEditData


class ContextGetRequest(
    GuardianBaseModel, NamePathMixin, NamespacePathMixin, AppNamePathMixin
): ...


class ContextsGetRequest(GuardianBaseModel, PaginationRequestMixin): ...


class ContextsByAppnameGetRequest(GuardianBaseModel, PaginationRequestMixin):
    app_name: str


class ContextsByNamespaceGetRequest(GuardianBaseModel, PaginationRequestMixin):
    namespace_name: str


#####
# Responses
#####


class Context(
    GuardianBaseModel,
    ResourceURLObjectMixin,
    DisplayNameObjectMixin,
    NamespacedObjectMixin,
): ...


class ContextSingleResponse(GuardianBaseModel):
    context: Context


class ContextMultipleResponse(GuardianBaseModel, PaginationObjectMixin):
    contexts: list[Context]
