# Copyright (C) 2023 Univention GmbH
#
# SPDX-License-Identifier: AGPL-3.0-only


from .base import (
    AppNameObjectMixin,
    AppNamePathMixin,
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


class NamespaceGetRequest(GuardianBaseModel, NamePathMixin, AppNamePathMixin): ...


class NamespacesGetRequest(GuardianBaseModel, PaginationRequestMixin): ...


class NamespacesByAppnameGetRequest(GuardianBaseModel, PaginationRequestMixin):
    app_name: str


class NamespaceCreateData(
    GuardianBaseModel, DisplayNameObjectMixin, NameObjectMixin
): ...


class NamespaceCreateRequest(GuardianBaseModel, AppNamePathMixin):
    data: NamespaceCreateData


class NamespaceEditData(GuardianBaseModel, DisplayNameObjectMixin): ...


class NamespaceEditRequest(NamespaceGetRequest):
    data: NamespaceEditData


#####
# Responses
#####


class Namespace(
    GuardianBaseModel,
    ResourceURLObjectMixin,
    DisplayNameObjectMixin,
    NameObjectMixin,
    AppNameObjectMixin,
): ...


class NamespaceSingleResponse(GuardianBaseModel):
    namespace: Namespace


class NamespaceMultipleResponse(GuardianBaseModel, PaginationObjectMixin):
    namespaces: list[Namespace]
