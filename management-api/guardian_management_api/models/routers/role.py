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


class RoleCreateData(GuardianBaseModel, DisplayNameObjectMixin, NameObjectMixin):
    ...


class RoleCreateRequest(CreateBaseRequest):
    data: RoleCreateData


class RoleEditData(GuardianBaseModel, DisplayNameObjectMixin):
    ...


class RoleEditRequest(EditBaseRequest):
    data: RoleEditData


#####
# Responses
#####


class Role(
    GuardianBaseModel,
    ResourceURLObjectMixin,
    DisplayNameObjectMixin,
    NamespacedObjectMixin,
):
    ...


class RoleSingleResponse(GuardianBaseModel):
    role: Role


class RoleMultipleResponse(GuardianBaseModel, PaginationObjectMixin):
    roles: list[Role]
