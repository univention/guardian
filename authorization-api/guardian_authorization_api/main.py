import os
from contextlib import asynccontextmanager

from fastapi import FastAPI
from loguru import logger

from .adapters.base import AdapterContainer
from .logging import configure_logger
from .ports import SettingsPort


@asynccontextmanager
async def lifespan(fastapi_app: FastAPI):
    await configure_logger()
    adapter_container = AdapterContainer.instance()
    settings_port = await adapter_container.get_adapter(SettingsPort)
    await configure_logger(settings_port)
    logger.info(
        f"Starting Guardian Authorization API with working dir '{os.getcwd()}'."
    )
    await adapter_container.initialize_adapters()
    yield


app = FastAPI(lifespan=lifespan)
