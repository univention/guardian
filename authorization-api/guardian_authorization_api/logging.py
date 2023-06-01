import os
import sys
from enum import Enum
from typing import Optional

from loguru import logger
from pydantic import BaseSettings


class LogLevel(str, Enum):
    TRACE = "TRACE"
    DEBUG = "DEBUG"
    INFO = "INFO"
    SUCCESS = "SUCCESS"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


class LoggingSettings(BaseSettings):
    structured: bool = False
    level: LogLevel = LogLevel.SUCCESS
    log_format: str = (
        "<green>{time:YYYY-MM-DD HH:mm:ss.SSS ZZ}</green> | <level>{level}</level> | "
        "<level>{message}</level> | {extra}"
    )

    class Config:
        env_prefix = "GUARDIAN_AUTHZ_LOGGING_"
        env_file = os.getenv(
            "GUARDIAN_AUTHZ_ENV_FILE",
            os.path.join(os.getenv("SERVICE_DIR", ""), ".env"),
        )


def configure_logger(logging_settings: Optional[LoggingSettings] = None):
    if logging_settings is None:
        logging_settings = LoggingSettings()
    logger.remove()
    logger.add(
        sys.stderr,
        format=logging_settings.log_format,
        serialize=logging_settings.structured,
        level=logging_settings.level,
        colorize=not logging_settings.structured,
    )
