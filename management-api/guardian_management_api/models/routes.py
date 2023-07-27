# Copyright (C) 2023 Univention GmbH
#
# SPDX-License-Identifier: AGPL-3.0-only


from fastapi import Path
from pydantic import BaseModel, Field
from pydantic.networks import AnyHttpUrl

from .role import ResponseRole


class GuardianBaseModel(BaseModel):
    class Config:
        allow_population_by_field_name = True


MANAGEMENT_OBJECT_NAME_REGEX = r"[a-z][a-z0-9\-_]*"


class ManagementObjectName(GuardianBaseModel):
    """Name of an app"""

    __root__: str = Field(
        example="kelvin-rest-api", regex=MANAGEMENT_OBJECT_NAME_REGEX, min_length=1
    )


class ManagementAppCreateRequest(GuardianBaseModel):
    name: ManagementObjectName = Field(..., description="Name of the app to create.")
    display_name: str | None = Field(
        None, description="Display name of the app to create."
    )


class AppAdminResponse(GuardianBaseModel):
    name: ManagementObjectName = Field(..., description="Name of the app admin.")
    display_name: str | None = Field(None, description="Display name of the app admin.")
    role: ResponseRole = Field(..., description="Role of the app admin.")


class ManagementAppCreateResponse(GuardianBaseModel):
    name: ManagementObjectName = Field(..., description="Name of the created app.")
    display_name: str | None = Field(
        None, description="Display name of the app to create."
    )
    resource_url: AnyHttpUrl = Field(..., description="URL to the created app.")
    app_admin: AppAdminResponse = Field(
        ..., description="App admin role of the created app."
    )


class ManagementAppGetResponse(GuardianBaseModel):
    name: ManagementObjectName = Field(..., description="Name of the app.")
    display_name: str | None = Field(
        None, description="Display name of the app to create."
    )
    resource_url: AnyHttpUrl = Field(..., description="URL to the created app.")
    app_admin: AppAdminResponse = Field(
        ..., description="App admin role of the created app."
    )


class ManagementAppGetRequest(GuardianBaseModel):
    name: str = Path(
        ..., description="Name of the app to get.", regex=MANAGEMENT_OBJECT_NAME_REGEX
    )
