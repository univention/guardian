import sys
from dataclasses import dataclass
from enum import StrEnum
from typing import Optional

from loguru import logger

from guardian_authorization_api.ports import SettingsPort


class LogLevel(StrEnum):
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


LOG_FORMAT_SETTING_NAME = "guardian.authz.logging.format"
STRUCTURED_SETTING_NAME = "guardian.authz.logging.structured"
LOG_LEVEL_SETTING_NAME = "guardian.authz.logging.level"
BACKTRACE_SETTING_NAME = "guardian.authz.logging.backtrace"
DIAGNOSE_SETTING_NAME = "guardian.authz.logging.diagnose"


@dataclass
class LoggingDefaultSettings:
    format: str = (
        "<green>{time:YYYY-MM-DD HH:mm:ss.SSS ZZ}</green> | <level>{level}</level> "
        "| <level>{message}</level> | {extra}"
    )
    level: str = "INFO"
    structured: bool = False
    backtrace: bool = False
    diagnose: bool = False


async def configure_logger(settings_port: Optional[SettingsPort] = None):
    settings = LoggingDefaultSettings()
    if settings_port:
        settings.format = await settings_port.get_setting(
            LOG_FORMAT_SETTING_NAME, str, settings.format
        )
        settings.level = await settings_port.get_setting(
            LOG_LEVEL_SETTING_NAME, str, settings.level
        )
        settings.structured = await settings_port.get_setting(
            STRUCTURED_SETTING_NAME, bool, settings.structured
        )
        settings.backtrace = await settings_port.get_setting(
            BACKTRACE_SETTING_NAME, bool, settings.backtrace
        )
        settings.diagnose = await settings_port.get_setting(
            DIAGNOSE_SETTING_NAME, bool, settings.diagnose
        )
    level = LogLevel(settings.level)
    logger.remove()
    logger.add(
        sys.stderr,
        format=settings.format,
        serialize=settings.structured,
        level=level,
        colorize=not settings.structured,
        enqueue=True,
        backtrace=settings.backtrace,
        diagnose=settings.diagnose,
    )
