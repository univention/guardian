from guardian_management_api.models.authz import Actor, OperationType, Resource
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
