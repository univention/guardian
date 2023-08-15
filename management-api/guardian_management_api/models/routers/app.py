# Copyright (C) 2023 Univention GmbH
#
# SPDX-License-Identifier: AGPL-3.0-only

from pydantic import Field

from ...models.routers.base import (
    DisplayNameObjectMixin,
    GuardianBaseModel,
    ManagementObjectName,
    NameObjectMixin,
    NamePathMixin,
    PaginationObjectMixin,
    ResourceURLObjectMixin,
)
from ...models.routers.role import Role as ResponseRole

#####
# Requests
#####


class AppCreateRequest(GuardianBaseModel):
    name: ManagementObjectName = Field(..., description="Name of the app to create.")
    display_name: str | None = Field(
        None, description="Display name of the app to create."
    )


class AppGetRequest(GuardianBaseModel, NamePathMixin):
    ...


class AppEditData(GuardianBaseModel, DisplayNameObjectMixin):
    ...


class AppEditRequest(AppGetRequest):
    data: AppEditData


#####
# Responses
#####


class AppAdmin(GuardianBaseModel, DisplayNameObjectMixin, NameObjectMixin):
    role: ResponseRole = Field(..., description="Role of the app admin.")


class App(
    GuardianBaseModel, ResourceURLObjectMixin, DisplayNameObjectMixin, NameObjectMixin
):
    app_admin: AppAdmin | None = Field(
        None, description="App admin role of the created app."
    )


class AppSingleResponse(GuardianBaseModel):
    app: App


class AppMultipleResponse(GuardianBaseModel, PaginationObjectMixin):
    apps: list[App]
