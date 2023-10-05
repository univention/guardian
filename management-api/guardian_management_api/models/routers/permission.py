# Copyright (C) 2023 Univention GmbH
#
# SPDX-License-Identifier: AGPL-3.0-only

from .base import (
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


class PermissionGetRequest(
    GuardianBaseModel, NamePathMixin, NamespacePathMixin, AppNamePathMixin
):
    ...


class PermissionsGetRequest(GuardianBaseModel, PaginationRequestMixin):
    ...


class PermissionCreateData(GuardianBaseModel, DisplayNameObjectMixin, NameObjectMixin):
    ...


class PermissionCreateRequest(CreateBaseRequest):
    data: PermissionCreateData


class PermissionEditData(GuardianBaseModel, DisplayNameObjectMixin):
    ...


class PermissionEditRequest(EditBaseRequest):
    data: PermissionEditData


#####
# Responses
#####


class FastAPIPermission(
    GuardianBaseModel,
    ResourceURLObjectMixin,
    DisplayNameObjectMixin,
    NamespacedObjectMixin,
):
    ...


class PermissionSingleResponse(GuardianBaseModel):
    permission: FastAPIPermission


class PermissionMultipleResponse(GuardianBaseModel, PaginationObjectMixin):
    permissions: list[FastAPIPermission]
