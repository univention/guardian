# Copyright (C) 2023 Univention GmbH
#
# SPDX-License-Identifier: AGPL-3.0-only
import os
from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI
from fastapi.responses import ORJSONResponse
from guardian_lib.adapter_registry import ADAPTER_REGISTRY, port_dep
from guardian_lib.ports import AuthenticationPort, SettingsPort
from loguru import logger

from .adapter_registry import configure_registry, initialize_adapters
from .logging import configure_logger
from .routes import router


@asynccontextmanager
async def lifespan(fastapi_app: FastAPI):
    await configure_logger()
    configure_registry(ADAPTER_REGISTRY)
    settings_port = await ADAPTER_REGISTRY.request_port(SettingsPort)
    await configure_logger(settings_port)
    logger.info(
        f"Starting Guardian Authorization API with working dir '{os.getcwd()}'."
    )
    await initialize_adapters(ADAPTER_REGISTRY)
    auth_adapter = await port_dep(AuthenticationPort)()
    fastapi_app.include_router(
        router, prefix=API_PREFIX, dependencies=[Depends(auth_adapter)]
    )
    yield


API_PREFIX = os.environ.get("GUARDIAN__AUTHZ__API_PREFIX", "/guardian/authorization")
app = FastAPI(
    lifespan=lifespan,
    title="Guardian Authorization API",
    openapi_url=f"{API_PREFIX}/openapi.json",
    docs_url=f"{API_PREFIX}/docs",
    default_response_class=ORJSONResponse,
    swagger_ui_oauth2_redirect_url=f"{API_PREFIX}/docs/oauth2-redirect",
    swagger_ui_init_oauth={
        "usePkceWithAuthorizationCodeGrant": True,
        "clientId": "guardian",
        "scope": "openid",
    },
)
