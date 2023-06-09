from typing import Any, Iterable, Optional

import loguru
from opa_client.client import OPAClient  # type: ignore[import]

from guardian_authorization_api.errors import PolicyUpstreamError
from guardian_authorization_api.models.policies import (
    PolicyObject,
    Target,
    Permission,
    Context,
    CheckPermissionsResult,
    Policy,
    GetPermissionsResult,
    Namespace,
    TargetPermissions,
)
from guardian_authorization_api.models.settings import RequiredSetting
from guardian_authorization_api.ports import PolicyPort


EMPTY_TARGET = Target(
    old_target=PolicyObject(id="", attributes={}, roles=[]),
    new_target=PolicyObject(id="", attributes={}, roles=[]),
)


class OPAAdapter(PolicyPort):
    OPA_URL_SETTING_NAME = "opa_adapter.url"
    OPA_GET_PERMISSIONS_POLICY = "/v1/data/univention/base/get_permissions"

    def __init__(self, logger: "loguru.Logger"):
        super().__init__(logger)
        self._opa_url = ""
        self._opa_client = None

    @staticmethod
    def required_settings() -> Iterable[RequiredSetting]:
        return [RequiredSetting(OPAAdapter.OPA_URL_SETTING_NAME, str, None)]

    @property
    def is_cached(self):
        return True

    @property
    def opa_client(self):
        if self._opa_client is None:
            self._opa_client = OPAClient(self._opa_url)
        return self._opa_client

    async def configure(self, settings: dict[str, Any]):
        self._opa_url = settings[OPAAdapter.OPA_URL_SETTING_NAME]

    async def check_permissions(
        self,
        actor: PolicyObject,
        targets: Optional[Iterable[Target]] = None,
        target_permissions: Optional[set[Permission]] = None,
        general_permissions: Optional[set[Permission]] = None,
        context: Optional[set[Context]] = None,
        extra_args: Optional[dict[str, Any]] = None,
    ) -> CheckPermissionsResult:
        raise NotImplementedError

    async def get_permissions(
        self,
        actor: PolicyObject,
        targets: Optional[Iterable[Target]] = None,
        namespaces: Optional[Iterable[Namespace]] = None,
        contexts: Optional[Iterable[Context]] = None,
        extra_args: Optional[dict[str, Any]] = None,
        include_general_permissions: bool = False,
    ) -> GetPermissionsResult:
        if targets is None:
            targets = []
        if namespaces is None:
            namespaces = []
        if contexts is None:
            contexts = []
        if extra_args is None:
            extra_args = {}
        if include_general_permissions:
            targets = list(targets) + [EMPTY_TARGET]
        try:
            opa_response = await self.opa_client.check_policy(
                self.OPA_GET_PERMISSIONS_POLICY,
                data=dict(
                    actor=actor,
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
        raise NotImplementedError
