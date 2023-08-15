# Copyright (C) 2023 Univention GmbH
#
# SPDX-License-Identifier: AGPL-3.0-only

from fastapi import Path, Query
from pydantic import AnyHttpUrl, BaseModel, ConstrainedStr, Field


class GuardianBaseModel(BaseModel):
    class Config:
        allow_population_by_field_name = True


MANAGEMENT_OBJECT_NAME_REGEX = r"[a-z][a-z0-9\-_]*"


class ManagementObjectName(ConstrainedStr):
    """Name of an object"""

    regex = MANAGEMENT_OBJECT_NAME_REGEX
    min_length = 1


class PaginationInfo(GuardianBaseModel):
    """
    Contains information about the current pagination of the response.
    """

    offset: int = Field(
        ..., description="The offset at which the list of objects starts at."
    )
    limit: int = Field(..., description="The limit of objects per response.")
    total_count: int = Field(
        ..., description="The total amount of objects found for the request."
    )


class PaginationObjectMixin(BaseModel):
    """
    Mixin to add a pagination attribute to a model.
    """

    pagination: PaginationInfo


class RawCodeObjectMixin(BaseModel):
    code: str | None = Field(None, description="Raw code, as a base64 encoded string.")


class DocumentationObjectMixin(BaseModel):
    documentation: str | None = Field(
        None, description="A text documenting the condition."
    )


class DisplayNameObjectMixin(BaseModel):
    """
    Mixin to add a display name attribute to a model.
    """

    display_name: str | None = Field(None, description="Display name of the object.")


class NameObjectMixin(BaseModel):
    """
    Mixin to add a name attribute to a model.
    """

    name: ManagementObjectName = Field(..., description="Name of the object.")


class NamespaceNameObjectMixin(BaseModel):
    """
    Mixin to add a namespace name attribute to a model.
    """

    namespace_name: ManagementObjectName = Field(
        ..., description="Name of the namespace the object belongs to."
    )


class AppNameObjectMixin(BaseModel):
    """
    Mixin to add an app name attribute to a model.
    """

    app_name: ManagementObjectName = Field(
        ..., description="Name of the app the object belongs to."
    )


class ResourceURLObjectMixin(BaseModel):
    """
    Mixin to add a resource url attribute to a model.
    """

    resource_url: AnyHttpUrl = Field(..., description="URL of the object.")


class NamespacedObjectMixin(BaseModel):
    """
    Mixin to add app_name, namespace_name and name attributes to a model.
    """

    app_name: ManagementObjectName = Field(
        ..., description="Name of the app the object belongs to."
    )
    namespace_name: ManagementObjectName = Field(
        ..., description="Name of the namespace the object belongs to."
    )
    name: ManagementObjectName = Field(..., description="Name of the object.")


class AppNamePathMixin(BaseModel):
    """
    Mixin for request models, that dds an app name path parameter.
    """

    app_name: str = Path(
        ...,
        description="Name of the app the object belongs to.",
        pattern=MANAGEMENT_OBJECT_NAME_REGEX,
    )


class NamespacePathMixin(BaseModel):
    """
    Mixin for request models, that adds a namespace name path parameter.
    """

    namespace_name: str = Path(
        ...,
        description="Name of the namespace the object belongs to.",
        pattern=MANAGEMENT_OBJECT_NAME_REGEX,
    )


class NamePathMixin(BaseModel):
    """
    Mixin for request models, that adds a name path parameter.
    """

    name: str = Path(
        ...,
        description="Name of the object.",
        pattern=MANAGEMENT_OBJECT_NAME_REGEX,
    )


class PaginationRequestMixin(BaseModel):
    """
    Mixin for request models, that adds offset and limit query parameters
    for pagination.
    """

    offset: int = Query(0, description="The offset for the paginated result.")
    limit: int = Query(
        1000, description="The maximum amount of items to return in one response."
    )


class GetAllRequest(GuardianBaseModel, PaginationRequestMixin):
    """
    Default request model to query for all objects of a resource.

    It contains query parameters for pagination.
    """


class GetFullIdentifierRequest(
    GuardianBaseModel, AppNamePathMixin, NamespacePathMixin, NamePathMixin
):
    """
    Default request model to query for a specific object.

    Expects app name, namespace name and name as path parameters.
    """


class GetByNamespaceRequest(
    GuardianBaseModel, NamespacePathMixin, AppNamePathMixin, PaginationRequestMixin
):
    """
    Default request model to query for all objects in a specific namespace.

    Expects app name and namespace name as path parameters.
    """


class GetByAppRequest(GuardianBaseModel, AppNamePathMixin, PaginationRequestMixin):
    """
    Default request model to query for all objects in a specific app.

    Expects app name as path parameter.
    """


class CreateBaseRequest(GuardianBaseModel, NamespacePathMixin, AppNamePathMixin):
    """
    Default request model for object creation (POST). Should be used as a base class only.

    Expects app name and namespace name as path parameters.
    """


class EditBaseRequest(
    GuardianBaseModel, NamePathMixin, NamespacePathMixin, AppNamePathMixin
):
    """
    Default request model for object manipulation (PATCH). Should be used as a base class only.

    Expects app name, namespace name and name as path parameters.
    """
