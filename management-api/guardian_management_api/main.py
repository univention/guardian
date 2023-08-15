# Copyright (C) 2023 Univention GmbH
#
# SPDX-License-Identifier: AGPL-3.0-only
import os
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.responses import ORJSONResponse
from loguru import logger

from .adapter_registry import ADAPTER_REGISTRY, configure_registry, initialize_adapters
from .constants import API_PREFIX
from .logging import configure_logger
from .ports.settings import SettingsPort
from .routers.app import router as app_router
from .routers.namespace import router as namespace_router


@asynccontextmanager
async def lifespan(fastapi_app: FastAPI):
    await configure_logger()
    configure_registry(ADAPTER_REGISTRY)
    settings_port = await ADAPTER_REGISTRY.request_port(SettingsPort)
    await configure_logger(settings_port)
    logger.info(f"Starting Guardian Management API with working dir '{os.getcwd()}'.")
    await initialize_adapters(ADAPTER_REGISTRY)
    yield


app = FastAPI(
    lifespan=lifespan,
    title="Guardian Management API",
    openapi_url=f"{API_PREFIX}/openapi.json",
    docs_url=f"{API_PREFIX}/docs",
    default_response_class=ORJSONResponse,
)
app.include_router(app_router, prefix=API_PREFIX)
app.include_router(namespace_router, prefix=API_PREFIX)
