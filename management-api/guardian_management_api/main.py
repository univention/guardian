# Copyright (C) 2023 Univention GmbH
#
# SPDX-License-Identifier: AGPL-3.0-only
import asyncio
import logging
import os
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import ORJSONResponse
from guardian_lib.adapter_registry import ADAPTER_REGISTRY
from guardian_lib.ports import SettingsPort
from loguru import logger
from starlette.staticfiles import StaticFiles

from .adapter_registry import configure_registry, initialize_adapters
from .constants import API_PREFIX, BUNDLE_SERVER_DISABLED_SETTING_NAME
from .logging import configure_logger
from .ports.bundle_server import BundleServerPort, BundleType
from .ports.condition import ConditionPersistencePort
from .routers.app import router as app_router
from .routers.capability import router as capability_router
from .routers.condition import router as condition_router
from .routers.context import router as context_router
from .routers.custom_endpoint import router as custom_endpoint_router
from .routers.namespace import router as namespace_router
from .routers.permission import router as permission_router
from .routers.role import router as role_router


def mount_routers(fastapi_app: FastAPI):
    fastapi_app.include_router(app_router, prefix=API_PREFIX)
    fastapi_app.include_router(namespace_router, prefix=API_PREFIX)
    fastapi_app.include_router(role_router, prefix=API_PREFIX)
    fastapi_app.include_router(context_router, prefix=API_PREFIX)
    fastapi_app.include_router(permission_router, prefix=API_PREFIX)
    fastapi_app.include_router(condition_router, prefix=API_PREFIX)
    fastapi_app.include_router(capability_router, prefix=API_PREFIX)
    fastapi_app.include_router(custom_endpoint_router, prefix=API_PREFIX)


def mount_bundle_server(fastapi_app: FastAPI, bundle_dir: Path):
    fastapi_app.mount(
        f"{API_PREFIX}/bundles", StaticFiles(directory=bundle_dir), name="bundles"
    )


async def rebuild_bundle(
    bundle_server_port: BundleServerPort,
    condition_persistence_port: ConditionPersistencePort,
):  # pragma: no cover
    while True:
        try:
            await bundle_server_port.generate_bundles(condition_persistence_port)
        except Exception:
            logging.exception("Exception during bundle rebuild")
        await asyncio.sleep(bundle_server_port.get_check_interval())


@asynccontextmanager
async def lifespan(fastapi_app: FastAPI):
    await configure_logger()
    configure_registry(ADAPTER_REGISTRY)
    settings_port: SettingsPort = await ADAPTER_REGISTRY.request_port(SettingsPort)
    await configure_logger(settings_port)
    logger.info(f"Starting Guardian Management API with working dir '{os.getcwd()}'.")
    await initialize_adapters(ADAPTER_REGISTRY)
    logger.info("Mounting routers.")
    mount_routers(fastapi_app)
    rebuild_bundle_task = None
    if not await settings_port.get_setting(
        BUNDLE_SERVER_DISABLED_SETTING_NAME, bool, False
    ):
        logger.info("Mounting bundle server.")
        bundle_server_port: BundleServerPort = await ADAPTER_REGISTRY.request_port(
            BundleServerPort
        )
        cond_persistence_port = await ADAPTER_REGISTRY.request_port(
            ConditionPersistencePort
        )
        bundle_dir = await bundle_server_port.prepare_directories()
        mount_bundle_server(fastapi_app, bundle_dir)
        await bundle_server_port.generate_templates()
        await bundle_server_port.schedule_bundle_build(BundleType.data)
        await bundle_server_port.schedule_bundle_build(BundleType.policies)
        rebuild_bundle_task = asyncio.create_task(
            rebuild_bundle(bundle_server_port, cond_persistence_port)
        )
    yield
    if rebuild_bundle_task is not None:
        rebuild_bundle_task.cancel()


app = FastAPI(
    lifespan=lifespan,
    title="Guardian Management API",
    openapi_url=f"{API_PREFIX}/openapi.json",
    docs_url=f"{API_PREFIX}/docs",
    default_response_class=ORJSONResponse,
)
