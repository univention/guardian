# Copyright (C) 2023 Univention GmbH
#
# SPDX-License-Identifier: AGPL-3.0-only


from fastapi import Path
from pydantic import BaseModel, Field


class GuardianBaseModel(BaseModel):
    class Config:
        allow_population_by_field_name = True


class ManagementAppCreateRequest(GuardianBaseModel):
    name: str = Field(..., description="Name of the app to create.")
    display_name: str | None = Field(
        None, description="Display name of the app to create."
    )


class RoleResponse(GuardianBaseModel):
    namespace: str = Field(..., description="Namespace of the role.")
    name: str = Field(..., description="Name of the role.")
    display_name: str = Field(..., description="Display name of the role.")


class ManagementAppCreateResponse(GuardianBaseModel):
    name: str = Field(..., description="Name of the created app.")
    display_name: str | None = Field(
        None, description="Display name of the app to create."
    )
    resource_url: str = Field(..., description="URL to the created app.")
    app_admin: RoleResponse = Field(
        ..., description="App admin role of the created app."
    )


class ManagementAppGetResponse(GuardianBaseModel):
    name: str = Field(..., description="Name of the app.")
    display_name: str | None = Field(
        None, description="Display name of the app to create."
    )
    resource_url: str = Field(..., description="URL to the created app.")
    app_admin: RoleResponse = Field(
        ..., description="App admin role of the created app."
    )


class ManagementAppGetRequest(GuardianBaseModel):
    name: str = Path(..., description="Name of the app to get.")
