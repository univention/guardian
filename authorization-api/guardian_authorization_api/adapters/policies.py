# Copyright (C) 2023 Univention GmbH
#
# SPDX-License-Identifier: AGPL-3.0-only

from collections import defaultdict
from dataclasses import asdict
from typing import Any, Optional, Type

from opa_client.client import OPAClient
from port_loader import AsyncConfiguredAdapterMixin

from guardian_authorization_api.errors import PolicyUpstreamError
from guardian_authorization_api.models.policies import (
    CheckPermissionsQuery,
    CheckPermissionsResult,
    CheckResult,
    GetPermissionsQuery,
    GetPermissionsResult,
    Namespace,
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
    OPA_CHECK_PERMISSIONS_POLICY = "/v1/data/univention/base/check_permissions"

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

    def _process_namespaces(
        self, query_namespaces: Optional[list[Namespace]]
    ) -> dict[str, list[str]]:
        namespaces: dict[str, list[str]] = defaultdict(list)
        _query_namespaces: list[Namespace] = query_namespaces or []
        for namespace in _query_namespaces:
            namespaces[namespace.app_name].append(namespace.name)
        return namespaces

    async def check_permissions(
        self, query: CheckPermissionsQuery
    ) -> CheckPermissionsResult:
        targets = (
            []
            if query.targets is None
            else [
                {"old": target.old_target, "new": target.new_target}
                for target in query.targets
            ]
        )
        targets.append({"old": EMPTY_TARGET.old_target, "new": EMPTY_TARGET.new_target})
        namespaces: dict[str, list[str]] = self._process_namespaces(
            query_namespaces=query.namespaces
        )
        contexts = [] if query.contexts is None else query.contexts
        extra_args = {} if query.extra_args is None else query.extra_args
        try:
            opa_response = await self.opa_client.check_policy(
                self.OPA_CHECK_PERMISSIONS_POLICY,
                data={
                    "actor": query.actor,
                    "targets": targets,
                    "namespaces": namespaces,
                    "contexts": contexts,
                    "extra_args": extra_args,
                },
            )
        except Exception as exc:
            raise PolicyUpstreamError(
                "Upstream error while checking permissions."
            ) from exc
        target_permissions = []
        actor_has_general_permissions = False
        try:
            for result in opa_response:
                if result["target_id"] == "":
                    actor_has_general_permissions = result["result"]
                    continue
                target_permissions.append(
                    CheckResult(
                        target_id=result["target_id"],
                        actor_has_permissions=result["result"],
                    )
                )
            return CheckPermissionsResult(
                target_permissions=target_permissions,
                actor_has_general_permissions=actor_has_general_permissions,
            )
        except Exception as exc:
            raise PolicyUpstreamError(
                "Upstream returned faulty data for check_permissions."
            ) from exc

    def _format_roles(self, roles: list[dict[str, str]]) -> list[str]:
        return [
            f"{role['app_name']}:{role['namespace_name']}:{role['name']}"
            for role in roles
        ]

    async def get_permissions(self, query: GetPermissionsQuery) -> GetPermissionsResult:
        targets: list[dict[str, dict | None]] = (
            []
            if query.targets is None
            else [
                {
                    "old": asdict(target.old_target) if target.old_target else None,
                    "new": asdict(target.new_target) if target.new_target else None,
                }
                for target in query.targets
            ]
        )
        namespaces: dict[str, list[str]] = self._process_namespaces(
            query_namespaces=query.namespaces
        )
        contexts = [] if query.contexts is None else query.contexts
        extra_args = {} if query.extra_args is None else query.extra_args
        actor = asdict(query.actor)
        actor["roles"] = self._format_roles(actor["roles"])
        for target in targets:
            for key in ["old", "new"]:
                if target[key]:
                    target[key]["roles"] = self._format_roles(target[key]["roles"])  # type: ignore
        if query.include_general_permissions:
            targets = list(targets) + [
                {
                    "old": asdict(EMPTY_TARGET.old_target)
                    if EMPTY_TARGET.old_target
                    else None,
                    "new": asdict(EMPTY_TARGET.new_target)
                    if EMPTY_TARGET.new_target
                    else None,
                }
            ]
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
            for response in opa_response:
                target_id = response["target_id"]
                permissions = [
                    Permission(
                        app_name=perm["appName"],
                        namespace_name=perm["namespace"],
                        name=perm["permission"],
                    )
                    for perm in response.get("permissions")
                ]
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
