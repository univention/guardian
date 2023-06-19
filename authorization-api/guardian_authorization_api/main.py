import os
from contextlib import asynccontextmanager

from fastapi import FastAPI
from loguru import logger

from .adapter_registry import ADAPTER_REGISTRY, configure_registry, initialize_adapters
from .logging import configure_logger
from .ports import SettingsPort
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
    yield


app = FastAPI(lifespan=lifespan)
app.include_router(router)
