from dataclasses import dataclass, field
from typing import Any, Type

import httpx
import jwt
from authlib.integrations.httpx_client import AsyncOAuth2Client
from guardian_lib.adapters.authentication import get_oauth_settings
from port_loader import AsyncConfiguredAdapterMixin
from port_loader.models import SETTINGS_NAME_METADATA

from guardian_management_api.errors import AuthorizationError
from guardian_management_api.models.authz import (
    Actor,
    OperationType,
    Resource,
    ResourceType,
)
from guardian_management_api.ports.authz import ResourceAuthorizationPort


class AlwaysAuthorizedAdapter(ResourceAuthorizationPort):
    class Config:
        alias = "always"

    async def authorize_operation(
        self, actor: Actor, operation_type: OperationType, resources: list[Resource]
    ) -> dict[str, bool]:
        return {resource.id: True for resource in resources}


class NeverAuthorizedAdapter(ResourceAuthorizationPort):
    class Config:
        alias = "never"

    async def authorize_operation(
        self, actor: Actor, operation_type: OperationType, resources: list[Resource]
    ) -> dict[str, bool]:
        return {resource.id: False for resource in resources}


def _get_resource_target(resource: Resource) -> dict[str, str]:
    if resource.resource_type == ResourceType.APP:
        return {
            # we need the app_name because the current OPA model relies on it
            "app_name": resource.name,
            "namespace_name": "",
            "name": resource.name,
        }
    if not resource.app_name:
        raise RuntimeError("This resource must have an app name.")
    if resource.resource_type == ResourceType.NAMESPACE:
        return {
            "app_name": resource.app_name,
            "namespace_name": resource.name,
            "name": resource.name,
        }
    if not resource.namespace_name:
        raise RuntimeError("This resource must have a namespace name.")
    return {
        "app_name": resource.app_name,
        "namespace_name": resource.namespace_name,
        "name": resource.name,
    }


@dataclass
class GuardianAuthorizationAdapterSettings:
    well_known_url: str = field(
        metadata={SETTINGS_NAME_METADATA: "oauth_adapter.well_known_url"}
    )
    m2m_secret: str = field(
        metadata={SETTINGS_NAME_METADATA: "oauth_adapter.m2m_secret"}
    )
    authorization_api_url: str = field(
        metadata={
            SETTINGS_NAME_METADATA: "guardian.management.adapter.authorization_api_url"
        }
    )


class GuardianAuthorizationAdapter(
    ResourceAuthorizationPort, AsyncConfiguredAdapterMixin
):
    class Config:
        alias = "guardian"

    def __init__(self):
        self._settings = None

    @classmethod
    def get_settings_cls(cls) -> Type[GuardianAuthorizationAdapterSettings]:
        return GuardianAuthorizationAdapterSettings

    async def configure(self, settings: GuardianAuthorizationAdapterSettings) -> None:
        self._settings = settings
        timeout = 10
        self.oauth_settings: dict[str, Any] = await get_oauth_settings(
            settings.well_known_url, timeout=timeout
        )
        self.logger.debug("Loaded oauth settings", oauth_settings=self.oauth_settings)
        self.jwks_client = jwt.PyJWKClient(
            self.oauth_settings["jwks_uri"], timeout=timeout
        )
        super().__init__()

    async def authorize_operation(
        self,
        actor: Actor,
        operation_type: OperationType,
        resources: list[Resource],
        # the following argument is jsut for the ease of testing, it should not be used in prod
        # since it is not part of the port signature
        client: AsyncOAuth2Client | None = None,
    ) -> dict[str, bool]:
        """Query the Guardian Authorization API."""
        if not client:
            client = AsyncOAuth2Client("guardian-cli", self._settings.m2m_secret)
        # get an access token from the Guardian Management API
        await client.fetch_token(
            self.oauth_settings["mtls_endpoint_aliases"]["token_endpoint"],
        )

        # query the Guardian Authorization API with httpx and m2m credentials
        response = await client.post(
            f"{self._settings.authorization_api_url}/permissions/check/with-lookup",
            json={
                "actor": {"id": actor.id},
                "targets": [
                    {
                        "old_target": {
                            "id": resource.id,
                            "roles": [],
                            "attributes": _get_resource_target(resource),
                        },
                        "new_target": {
                            "id": resource.id,
                            "roles": [],
                            "attributes": {},
                        },
                    }
                    for resource in resources
                ],
                "targeted_permissions_to_check": [
                    {
                        "app_name": "guardian",
                        "namespace_name": "management-api",
                        "name": operation_type.value,
                    }
                ],
                "general_permissions_to_check": [],
                "extra_request_data": {},
            },
        )
        # check the response status code and raise a custom exception if needed
        try:
            response.raise_for_status()
        except httpx.HTTPStatusError:
            raise AuthorizationError(
                f"Unsuccessful response from the Authorization API: {response.json()}"
            )

        default_dict: dict[str, bool] = {}
        return {
            resource.id: next(
                filter(
                    lambda x: x["target_id"] == resource.id,
                    response.json()["permissions_check_results"],
                ),
                default_dict,
            ).get("actor_has_permissions", False)
            for resource in resources
        }
