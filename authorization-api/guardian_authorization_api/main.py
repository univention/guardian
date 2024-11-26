# Copyright (C) 2023 Univention GmbH
#
# SPDX-License-Identifier: AGPL-3.0-only
import os
from contextlib import asynccontextmanager
from importlib import metadata
from uuid import uuid4

from fastapi import Depends, FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import ORJSONResponse
from guardian_lib.adapter_registry import ADAPTER_REGISTRY
from guardian_lib.ports import AuthenticationPort, SettingsPort
from loguru import logger

from .adapter_registry import configure_registry, initialize_adapters
from .constants import API_PREFIX, CORS_ALLOWED_ORIGINS
from .correlation_id import correlation_id_ctx_var
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
    auth_adapter = await ADAPTER_REGISTRY.request_port(AuthenticationPort)
    fastapi_app.include_router(
        router, prefix=API_PREFIX, dependencies=[Depends(auth_adapter)]
    )
    yield


app = FastAPI(
    lifespan=lifespan,
    title="Guardian Authorization API",
    version=metadata.version("authorization-api"),
    openapi_url=f"{API_PREFIX}/openapi.json",
    docs_url=f"{API_PREFIX}/docs",
    default_response_class=ORJSONResponse,
    swagger_ui_oauth2_redirect_url=f"{API_PREFIX}/docs/oauth2-redirect",
    swagger_ui_init_oauth={
        "usePkceWithAuthorizationCodeGrant": True,
        "clientId": "guardian-ui",
        "scopes": ["openid"],
    },
)

CORRELATION_ID_HEADER_NAME = "X-Request-ID"


@app.middleware("http")
async def add_correlation_id(request: Request, call_next):
    """Add correlation id to request object and contextualize logger

    The contextualize method uses Python `contextvars` so the are unique to each thread/task.
    """

    correlation_id = request.headers.get(CORRELATION_ID_HEADER_NAME, str(uuid4()))
    correlation_id_ctx_var.set(correlation_id)

    with logger.contextualize(correlation_id=correlation_id):
        logger.trace(
            f"Setting correlation id for request {request.url} to {correlation_id}"
        )
        response = await call_next(request)
        response.headers[CORRELATION_ID_HEADER_NAME] = correlation_id
        return response


# FastAPI doesn't allow adding middleware after the app has been started,
# so unfortunately we can't put this in the lifespan to make use of the
# settings_port.
if CORS_ALLOWED_ORIGINS:
    origins = CORS_ALLOWED_ORIGINS.split(",")
    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_methods=["*"],
        allow_headers=["Authorization"],
    )
