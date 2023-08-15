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


class Permission(
    GuardianBaseModel,
    ResourceURLObjectMixin,
    DisplayNameObjectMixin,
    NamespacedObjectMixin,
):
    ...


class PermissionSingleResponse(GuardianBaseModel):
    permission: Permission


class PermissionMultipleResponse(GuardianBaseModel, PaginationObjectMixin):
    permissions: list[Permission]
