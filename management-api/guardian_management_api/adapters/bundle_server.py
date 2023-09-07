import asyncio
from asyncio import Lock, Queue, QueueEmpty, QueueFull
from dataclasses import dataclass, field
from pathlib import Path
from typing import Type

import aiofiles.os
import aioshutil
import orjson
from guardian_lib.models.settings import SETTINGS_NAME_METADATA
from port_loader import AsyncConfiguredAdapterMixin

from guardian_management_api.constants import DEFAULT_BUNDLE_SERVER_BASE_DIR
from guardian_management_api.errors import BundleBuildError, BundleGenerationIOError
from guardian_management_api.ports.bundle_server import BundleServerPort, BundleType

BUNDLE_SERVER_ADAPTER_BASE_DIR = "bundle_server_adapter.base_dir"

DUMMY_CONDITION = """
package guardian.conditions

import future.keywords.every
import future.keywords.if
import future.keywords.in

# CONDITION DATA
# This is the data that is passed to the condition
# condition_data = {
#         "actor": {},
#         "target": {
#              "old": {},
#              "new": {},
#         },
#         "namespaces": {},
#         "contexts": set(),
#         "extra_args": {},
#         "parameters": {},
# }

# This condition evaluates to true only if the parameter "result" is true
condition("only_if_param_result_true", parameters, condition_data) if {
	parameters.result == true
} else = false if true
"""

DUMMY_MAPPING_JSON = {
    "roleCapabilityMapping": {
        "ucsschool:users:teacher": [
            {
                "appName": "ucsschool",
                "conditions": [],
                "namespace": "users",
                "permissions": ["read_first_name", "read_last_name"],
                "relation": "AND",
            },
            {
                "appName": "ucsschool",
                "conditions": [
                    {
                        "name": "ucsschool_users_target_has_same_school",
                        "parameters": {},
                    },
                    {
                        "name": "target_has_role",
                        "parameters": {"role": "ucsschool:users:student"},
                    },
                ],
                "namespace": "users",
                "permissions": ["read_first_name", "write_password", "export"],
                "relation": "AND",
            },
            {
                "appName": "OX",
                "conditions": [],
                "namespace": "mail",
                "permissions": ["edit-spam-filter", "export"],
                "relation": "AND",
            },
        ]
    }
}


@dataclass
class BundleServerAdapterSettings:
    base_dir: str = field(
        default=DEFAULT_BUNDLE_SERVER_BASE_DIR,
        metadata={SETTINGS_NAME_METADATA: BUNDLE_SERVER_ADAPTER_BASE_DIR},
    )
    check_interval: int = field(
        default=5,
        metadata={SETTINGS_NAME_METADATA: "bundle_server_adapter.check_interval"},
    )
    data_bundle_name: str = field(
        default="GuardianDataBundle",
        metadata={SETTINGS_NAME_METADATA: "bundle_server_adapter.data_bundle_name"},
    )
    policy_bundle_name: str = field(
        default="GuardianPolicyBundle",
        metadata={SETTINGS_NAME_METADATA: "bundle_server_adapter.policy_bundle_name"},
    )


class BundleServerAdapter(BundleServerPort, AsyncConfiguredAdapterMixin):
    class Config:
        alias = "default"
        cached = True

    def __init__(self):
        self._check_interval_time = 5.0
        self._data_bundle_name = "GuardianDataBundle"
        self._policy_bundle_name = "GuardianPolicyBundle"
        self._base_dir = DEFAULT_BUNDLE_SERVER_BASE_DIR
        self._data_bundle_queue = Queue(1)
        self._build_lock = Lock()
        self._policies_bundle_queue = Queue(1)

    @classmethod
    def get_settings_cls(cls) -> Type[BundleServerAdapterSettings]:  # pragma: no cover
        return BundleServerAdapterSettings

    async def configure(self, settings: BundleServerAdapterSettings):
        self._check_interval_time = float(settings.check_interval)
        self._data_bundle_name = settings.data_bundle_name
        self._base_dir = settings.base_dir

    def get_check_interval(self) -> float:  # pragma: no cover
        return self._check_interval_time

    async def prepare_directories(self) -> Path:
        bundle_dir = Path(self._base_dir) / "bundles"
        template_dir = Path(self._base_dir) / "templates"
        build_dir = Path(self._base_dir) / "build"
        for directory in bundle_dir, template_dir, build_dir:
            try:
                await aiofiles.os.makedirs(directory)
            except FileExistsError:
                pass
            except Exception as exc:
                raise BundleGenerationIOError(
                    "IO error during preparation of directories"
                ) from exc
        return bundle_dir

    async def generate_templates(self):
        data_bundle_manifest = {"roots": ["guardian/mapping"]}
        policy_bundle_manifest = {"roots": ["guardian/conditions"]}
        try:
            data_bundle_dir = (
                Path(self._base_dir) / "templates" / self._data_bundle_name
            )
            policy_bundle_dir = (
                Path(self._base_dir) / "templates" / self._policy_bundle_name
            )
            try:
                await aiofiles.os.makedirs(
                    str(data_bundle_dir / "guardian" / "mapping")
                )
                await aiofiles.os.makedirs(
                    str(policy_bundle_dir / "guardian" / "conditions")
                )
            except FileExistsError:
                pass
            async with aiofiles.open(str(data_bundle_dir / ".manifest"), "wb") as file:
                await file.write(orjson.dumps(data_bundle_manifest))
            async with aiofiles.open(
                str(policy_bundle_dir / ".manifest"), "wb"
            ) as file:
                await file.write(orjson.dumps(policy_bundle_manifest))
            async with aiofiles.open(
                str(data_bundle_dir / "guardian" / "mapping" / "data.json"), "wb"
            ) as file:
                await file.write(orjson.dumps(DUMMY_MAPPING_JSON))
            async with aiofiles.open(
                str(policy_bundle_dir / "guardian" / "conditions" / "test.rego"), "w"
            ) as file:
                await file.write(DUMMY_CONDITION)
        except Exception:
            raise BundleGenerationIOError("Template could not be generated.")

    async def _build_bundle(self, bundle_name: str):
        local_logger = self.logger.bind(
            bundle_name=bundle_name, base_dir=self._base_dir
        )
        local_logger.debug("Generating bundle.")
        base_dir = Path(self._base_dir)
        try:
            await aioshutil.rmtree(base_dir / "build" / bundle_name)
        except FileNotFoundError:
            local_logger.debug("build directory was not found. No need for cleanup")
        await aioshutil.copytree(
            base_dir / "templates" / bundle_name, base_dir / "build" / bundle_name
        )
        build_cmd = (
            f"opa build -b {base_dir / 'build' / bundle_name} -o "
            f"{base_dir / 'bundles' / bundle_name}.tar.gz"
        )
        local_logger = local_logger.bind(build_cmd=build_cmd)
        local_logger.debug("Building opa bundle.")
        build_proc = await asyncio.create_subprocess_shell(build_cmd)
        await build_proc.communicate()
        if build_proc.returncode != 0:
            raise BundleBuildError("Error during build of OPA bundles.")

    async def generate_bundles(self):
        async with self._build_lock:
            try:
                self._data_bundle_queue.get_nowait()
                await self._build_bundle(self._data_bundle_name)
                self._data_bundle_queue.task_done()
            except QueueEmpty:
                self.logger.debug("No data bundle scheduled for generation.")
            try:
                self._policies_bundle_queue.get_nowait()
                await self._build_bundle(self._policy_bundle_name)
                self._policies_bundle_queue.task_done()
            except QueueEmpty:
                self.logger.debug("No policy bundle scheduled for generation.")

    async def schedule_bundle_build(self, bundle_type: BundleType):
        try:
            if bundle_type == BundleType.data:
                self._data_bundle_queue.put_nowait(bundle_type)
            if bundle_type == BundleType.policies:
                self._policies_bundle_queue.put_nowait(bundle_type)
        except QueueFull:
            self.logger.debug(
                "Queue for bundle generation is already full."
            )  # We do not care about a full queue.