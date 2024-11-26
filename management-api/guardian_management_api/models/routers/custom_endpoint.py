# Copyright (C) 2023 Univention GmbH
#
# SPDX-License-Identifier: AGPL-3.0-only

from guardian_management_api.models.routers.base import (
    CreateBaseRequest,
    DisplayNameObjectMixin,
    DocumentationObjectMixin,
    EditBaseRequest,
    GuardianBaseModel,
    NameObjectMixin,
    NamespacedObjectMixin,
    PaginationObjectMixin,
    RawCodeObjectMixin,
    ResourceURLObjectMixin,
)

#####
# Requests
#####


class CustomEndpointCreateData(
    GuardianBaseModel,
    RawCodeObjectMixin,
    DocumentationObjectMixin,
    DisplayNameObjectMixin,
    NameObjectMixin,
): ...


class CustomEndpointCreateRequest(CreateBaseRequest):
    data: CustomEndpointCreateData


class CustomEndpointEditData(
    GuardianBaseModel,
    RawCodeObjectMixin,
    DocumentationObjectMixin,
    DisplayNameObjectMixin,
): ...


class CustomEndpointEditRequest(EditBaseRequest):
    data: CustomEndpointEditData


#####
# Responses
#####


class CustomEndpoint(
    GuardianBaseModel,
    DocumentationObjectMixin,
    ResourceURLObjectMixin,
    DisplayNameObjectMixin,
    NamespacedObjectMixin,
): ...


class CustomEndpointSingleResponse(GuardianBaseModel):
    custom_endpoint: CustomEndpoint


class CustomEndpointMultipleResponse(GuardianBaseModel, PaginationObjectMixin):
    custom_endpoints: list[CustomEndpoint]
