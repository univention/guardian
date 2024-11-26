# Copyright (C) 2023 Univention GmbH
#
# SPDX-License-Identifier: AGPL-3.0-only


from pydantic import Field

from ...models.routers.base import (
    AppNameObjectMixin,
    DisplayNameObjectMixin,
    GuardianBaseModel,
    ManagementObjectName,
    NameObjectMixin,
    NamePathMixin,
    NamespacedObjectMixin,
    PaginationObjectMixin,
    PaginationRequestMixin,
    ResourceURLObjectMixin,
)

#####
# Requests
#####


class AppCreateRequest(GuardianBaseModel):
    name: ManagementObjectName = Field(..., description="Name of the app to create.")
    display_name: str | None = Field(
        None, description="Display name of the app to create."
    )


class AppGetRequest(GuardianBaseModel, NamePathMixin): ...


class AppEditData(GuardianBaseModel, DisplayNameObjectMixin): ...


class AppEditRequest(AppGetRequest):
    data: AppEditData


class AppsGetRequest(GuardianBaseModel, PaginationRequestMixin): ...


#####
# Responses
#####


class AppAdmin(
    GuardianBaseModel,
    ResourceURLObjectMixin,
    DisplayNameObjectMixin,
    NamespacedObjectMixin,
): ...


class AppDefaultNamespace(
    ResourceURLObjectMixin, DisplayNameObjectMixin, AppNameObjectMixin, NameObjectMixin
): ...


class App(
    GuardianBaseModel, ResourceURLObjectMixin, DisplayNameObjectMixin, NameObjectMixin
): ...


class AppSingleResponse(GuardianBaseModel):
    app: App


class AppRegisterResponse(GuardianBaseModel):
    app: App
    admin_role: AppAdmin
    default_namespace: AppDefaultNamespace


class AppMultipleResponse(GuardianBaseModel, PaginationObjectMixin):
    apps: list[App]
