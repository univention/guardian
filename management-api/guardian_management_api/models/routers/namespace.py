# Copyright (C) 2023 Univention GmbH
#
# SPDX-License-Identifier: AGPL-3.0-only

from fastapi import Body, Path
from pydantic import AnyHttpUrl, Field

from .base import (
    MANAGEMENT_OBJECT_NAME_REGEX,
    GuardianBaseModel,
    ManagementObjectName,
    PaginationInfo,
    PaginationRequestMixin,
)

#####
# Requests
#####


class NamespaceGetByAppRequest(GuardianBaseModel, PaginationRequestMixin):
    app_name: str = Path(
        ...,
        description="Name of the app the namespace belongs to.",
        regex=MANAGEMENT_OBJECT_NAME_REGEX,
    )


class NamespaceGetRequest(GuardianBaseModel):
    app_name: str = Path(
        ...,
        description="Name of the app the namespace belongs to.",
        regex=MANAGEMENT_OBJECT_NAME_REGEX,
    )
    name: str = Path(
        ...,
        description="Name of the namespace.",
        regex=MANAGEMENT_OBJECT_NAME_REGEX,
    )


class NamespaceCreateData(GuardianBaseModel):
    name: str = Field(
        ...,
        description="Name of the namespace to create.",
        regex=MANAGEMENT_OBJECT_NAME_REGEX,
    )
    display_name: str | None = Field(
        None, description="Display name of the namespace to create"
    )


class NamespaceCreateRequest(GuardianBaseModel):
    app_name: str = Path(
        ...,
        description="Name of the app the namespace belongs to.",
        regex=MANAGEMENT_OBJECT_NAME_REGEX,
    )
    data: NamespaceCreateData


class NamespaceEditData(GuardianBaseModel):
    display_name: str | None = Body(
        None, description="New display name of the namespace."
    )


class NamespaceEditRequest(NamespaceGetRequest):
    data: NamespaceEditData


#####
# Responses
#####


class Namespace(GuardianBaseModel):
    name: ManagementObjectName = Field(..., description="Name of the namespace.")
    app_name: str = Field(..., description="Name of the app the namespace belongs to.")
    display_name: str | None = Field(None, description="Display name of the namespace.")
    resource_url: AnyHttpUrl = Field(..., description="URL to the created app.")


class NamespaceSingleResponse(GuardianBaseModel):
    namespace: Namespace


class NamespaceMultipleResponse(GuardianBaseModel):
    namespaces: list[Namespace]
    pagination: PaginationInfo
