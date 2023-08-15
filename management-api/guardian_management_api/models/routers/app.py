from fastapi import Path
from pydantic import AnyHttpUrl, Field

from guardian_management_api.models.role import ResponseRole
from guardian_management_api.models.routers.base import (
    MANAGEMENT_OBJECT_NAME_REGEX,
    GuardianBaseModel,
    ManagementObjectName,
)

#####
# Requests
#####


class AppCreateRequest(GuardianBaseModel):
    name: ManagementObjectName = Field(..., description="Name of the app to create.")
    display_name: str | None = Field(
        None, description="Display name of the app to create."
    )


class AppGetRequest(GuardianBaseModel):
    name: str = Path(
        ..., description="Name of the app to get.", regex=MANAGEMENT_OBJECT_NAME_REGEX
    )


#####
# Responses
#####


class AppAdmin(GuardianBaseModel):
    name: ManagementObjectName = Field(..., description="Name of the app admin.")
    display_name: str | None = Field(None, description="Display name of the app admin.")
    role: ResponseRole = Field(..., description="Role of the app admin.")


class App(GuardianBaseModel):
    name: ManagementObjectName = Field(..., description="Name of the created app.")
    display_name: str | None = Field(
        None, description="Display name of the app to create."
    )
    resource_url: AnyHttpUrl = Field(..., description="URL to the created app.")
    app_admin: AppAdmin = Field(..., description="App admin role of the created app.")


class AppSingleResponse(GuardianBaseModel):
    app: App
