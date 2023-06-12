import os
from contextlib import asynccontextmanager

from fastapi import FastAPI
from loguru import logger

from .adapters.base import ADAPTER_REGISTRY, configure_registry, initialize_adapters
from .logging import configure_logger
from .ports import SettingsPort


@asynccontextmanager
async def lifespan(fastapi_app: FastAPI):
    await configure_logger()
    configure_registry(ADAPTER_REGISTRY)
    settings_port = await ADAPTER_REGISTRY.get_adapter(SettingsPort)
    await configure_logger(settings_port)
    logger.info(
        f"Starting Guardian Authorization API with working dir '{os.getcwd()}'."
    )
    await initialize_adapters(ADAPTER_REGISTRY)
    yield


app = FastAPI(lifespan=lifespan)
