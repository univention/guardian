# Copyright (C) 2023 Univention GmbH
#
# SPDX-License-Identifier: AGPL-3.0-only


from guardian_management_api.models.routers.base import (
    CreateBaseRequest,
    DisplayNameObjectMixin,
    EditBaseRequest,
    GetAllRequest,
    GetByAppRequest,
    GetByNamespaceRequest,
    GetFullIdentifierRequest,
    GuardianBaseModel,
    NameObjectMixin,
    NamespacedObjectMixin,
    PaginationObjectMixin,
    ResourceURLObjectMixin,
)

#####
# Requests
#####


# request for route: GET .../roles/{app_name}/{namepace_name}/{name}
class RoleGetFullIdentifierRequest(GetFullIdentifierRequest):
    ...


class RoleCreateData(GuardianBaseModel, DisplayNameObjectMixin, NameObjectMixin):
    ...


# request for route: POST .../roles/{app_name}/{namespace_name}
class RoleCreateRequest(CreateBaseRequest):
    data: RoleCreateData


class RoleEditData(GuardianBaseModel, DisplayNameObjectMixin):
    ...


# request for route: PATCH .../roles/{app_name}/{namepace_name}/{name}
class RoleEditRequest(EditBaseRequest):
    data: RoleEditData


# request for route: GET .../roles
class RoleGetAllRequest(GetAllRequest):
    ...


# request for route: GET .../roles/{app_name}
class RoleGetByAppRequest(GetByAppRequest):
    ...


# request for route: GET .../roles/{app_name}/{namespace_name}
class RoleGetByNamespaceRequest(GetByNamespaceRequest):
    ...


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
