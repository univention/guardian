import os
from contextlib import asynccontextmanager

from fastapi import FastAPI
from loguru import logger

from .adapters import AdapterContainer
from .logging import configure_logger


@asynccontextmanager
async def lifespan(fastapi_app: FastAPI):
    configure_logger()
    logger.info(
        f"Starting Guardian Authorization API with working dir '{os.getcwd()}'."
    )
    adapter_container = AdapterContainer.instance()
    await adapter_container.initialize_adapters()
    yield


app = FastAPI(lifespan=lifespan)
