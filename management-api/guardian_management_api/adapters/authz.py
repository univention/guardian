import httpx
from authlib.integrations.httpx_client import AsyncOAuth2Client

from guardian_management_api.errors import AuthorizationError
from guardian_management_api.models.authz import (
    Actor,
    OperationType,
    Resource,
    ResourceType,
)
from guardian_management_api.ports.authz import ResourceAuthorizationPort


class AlwaysAuthorizedAdapter(ResourceAuthorizationPort):
    async def authorize_operation(
        self, actor: Actor, operation_type: OperationType, resources: list[Resource]
    ) -> dict[str, bool]:
        return {resource.id: True for resource in resources}


class NeverAuthorizedAdapter(ResourceAuthorizationPort):
    async def authorize_operation(
        self, actor: Actor, operation_type: OperationType, resources: list[Resource]
    ) -> dict[str, bool]:
        return {resource.id: False for resource in resources}


def _get_resource_target(resource: Resource) -> dict[str, str]:
    if resource.resource_type == ResourceType.APP:
        return {
            "app_name": resource.name,
            "name": resource.name,
        }
    if not resource.app_name:
        raise RuntimeError("This resource must have an app name.")
    if resource.resource_type == ResourceType.NAMESPACE:
        return {
            "app_name": resource.app_name,
            "name": resource.name,
        }
    if not resource.namespace_name:
        raise RuntimeError("This resource must have a namespace name.")
    return {
        "app_name": resource.app_name,
        "namespace_name": resource.namespace_name,
        "name": resource.name,
    }


class GuardianAuthorizationAdapter(ResourceAuthorizationPort):
    async def authorize_operation(
        self,
        actor: Actor,
        operation_type: OperationType,
        resources: list[Resource],
        client: AsyncOAuth2Client = AsyncOAuth2Client("guardian-cli", "univention"),
    ) -> dict[str, bool]:
        """Query the Guardian Authorization API."""
        # get an access token from the Guardian Management API
        await client.fetch_token(
            "http://traefik/guardian/keycloak/realms/GuardianDev/protocol/openid-connect/token",
        )

        # query the Guardian Authorization API with httpx and m2m credentials
        response = await client.post(
            "http://localhost/guardian/authorization/permissions/check/with-lookup",
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

        return {
            resource.id: next(  # type: ignore
                filter(
                    lambda x: x["target_id"] == resource.id,
                    response.json()["permissions_check_results"],
                ),
                {},
            ).get("actor_has_permissions", False)
            for resource in resources
        }
