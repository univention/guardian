from typing import Any, Iterable

from port_loader.utils import inject_port, injected_port

from ..models.incoming import GetPermissionAPIResponse, GetPermissionAPIResult
from ..models.policies import Context, Namespace, PolicyObject, Target
from ..ports import GetPermissionAPIPort, PolicyPort


class GetPermissionAPIAdapter(GetPermissionAPIPort):
    @inject_port(policy_port=PolicyPort)
    async def get_permissions(
        self,
        actor: PolicyObject,
        targets: Iterable[Target],
        contexts: Iterable[Context],
        extra_request_data: dict[str, Any],
        namespaces: Iterable[Namespace],
        include_general_permissions: bool,
        policy_port: PolicyPort = injected_port(PolicyPort),
    ) -> GetPermissionAPIResponse:
        result = await policy_port.get_permissions(
            actor,
            targets,
            namespaces,
            contexts,
            extra_args=extra_request_data,
            include_general_permissions=include_general_permissions,
        )
        return GetPermissionAPIResponse(
            target_permissions=[
                GetPermissionAPIResult(
                    target_id=target_permission.target_id,
                    permissions=target_permission.permissions,
                )
                for target_permission in result.target_permissions
            ],
            general_permissions=result.general_permissions,
        )
