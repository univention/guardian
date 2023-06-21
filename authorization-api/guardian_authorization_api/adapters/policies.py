from typing import Any, Optional, Type

from opa_client.client import OPAClient
from port_loader import AsyncConfiguredAdapterMixin

from guardian_authorization_api.errors import PolicyUpstreamError
from guardian_authorization_api.models.policies import (
    CheckPermissionsQuery,
    CheckPermissionsResult,
    GetPermissionsQuery,
    GetPermissionsResult,
    OPAAdapterSettings,
    Permission,
    Policy,
    PolicyObject,
    Target,
    TargetPermissions,
)
from guardian_authorization_api.ports import PolicyPort

EMPTY_TARGET = Target(
    old_target=PolicyObject(id="", attributes={}, roles=[]),
    new_target=PolicyObject(id="", attributes={}, roles=[]),
)


class OPAAdapter(PolicyPort, AsyncConfiguredAdapterMixin):
    OPA_GET_PERMISSIONS_POLICY = "/v1/data/univention/base/get_permissions"

    class Config:
        is_cached = True
        alias = "opa"

    def __init__(self):
        self._opa_url = ""
        self._opa_client = None

    @classmethod
    def get_settings_cls(cls) -> Type[OPAAdapterSettings]:
        return OPAAdapterSettings

    async def configure(self, settings: OPAAdapterSettings):
        self._opa_url = settings.opa_url

    @property
    def opa_client(self):  # pragma: no cover
        if self._opa_client is None:
            self._opa_client = OPAClient(self._opa_url)
        return self._opa_client

    async def check_permissions(
        self, query: CheckPermissionsQuery
    ) -> CheckPermissionsResult:
        raise NotImplementedError  # pragma: no cover

    async def get_permissions(self, query: GetPermissionsQuery) -> GetPermissionsResult:
        targets = [] if query.targets is None else query.targets
        namespaces = [] if query.namespaces is None else query.namespaces
        contexts = [] if query.contexts is None else query.contexts
        extra_args = {} if query.extra_args is None else query.extra_args
        if query.include_general_permissions:
            targets = list(targets) + [EMPTY_TARGET]
        try:
            opa_response = await self.opa_client.check_policy(
                self.OPA_GET_PERMISSIONS_POLICY,
                data=dict(
                    actor=query.actor,
                    targets=targets,
                    namespaces=namespaces,
                    contexts=contexts,
                    extra_args=extra_args,
                ),
            )
        except Exception as exc:
            raise PolicyUpstreamError(
                "Upstream error while getting permissions."
            ) from exc
        target_permissions = []
        general_permissions = None
        try:
            for result in opa_response:
                target_id = result["target_id"]
                permissions = [Permission(**perm) for perm in result.get("permissions")]
                if target_id == "":
                    general_permissions = permissions
                else:
                    target_permissions.append(
                        TargetPermissions(target_id=target_id, permissions=permissions)
                    )
            return GetPermissionsResult(
                actor=query.actor,
                target_permissions=target_permissions,
                general_permissions=general_permissions,
            )
        except Exception as exc:
            raise PolicyUpstreamError(
                "Upstream returned faulty data for get_permissions."
            ) from exc

    async def custom_policy(
        self, policy: Policy, data: Optional[dict[str, Any]] = None
    ) -> dict[str, Any]:
        raise NotImplementedError  # pragma: no cover
