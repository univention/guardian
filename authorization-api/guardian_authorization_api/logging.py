# Copyright (C) 2023 Univention GmbH
#
# SPDX-License-Identifier: AGPL-3.0-only

import logging
import sys
from dataclasses import dataclass
from enum import StrEnum
from typing import Optional

import port_loader
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
    level: str = "DEBUG"
    structured: bool = False
    backtrace: bool = False
    diagnose: bool = False


class InterceptHandler(logging.Handler):  # pragma: no cover
    """
    Copied from https://loguru.readthedocs.io/en/stable/overview.html#entirely-compatible-with-standard-logging

    This intercept handler catches all log messages from the standard logging
    library and redirects them to Loguru.

    This allows us to configure loggers from libraries we use to adhere to the same formatting and sinks
    (targets like files, stdout) we configured for our logs.
    This is done by `logging.get_logger("LOGGER_NAME").handlers = [InterceptHandler()]`

    This should be done during our logging setup for all loggers we want to intercept in this way.
    """

    def emit(self, record):
        # Get corresponding Loguru level if it exists.
        try:
            level = logger.level(record.levelname).name
        except ValueError:
            level = record.levelno

        # Find caller from where originated the logged message.
        frame, depth = sys._getframe(6), 6
        while frame and frame.f_code.co_filename == logging.__file__:
            frame = frame.f_back
            depth += 1

        logger.opt(depth=depth, exception=record.exc_info).log(
            level, record.getMessage()
        )


async def configure_logger(settings_port: Optional[SettingsPort] = None):
    for logger_name in ("uvicorn", "uvicorn.error", "uvicorn.access", "fastapi"):
        _logger = logging.getLogger(logger_name)
        _logger.handlers = [InterceptHandler()]
    logger.enable(port_loader.__name__)
    settings = LoggingDefaultSettings()
    if (
        settings_port
    ):  # pragma: no cover  here we just read from the settings port, which is tested elsewhere
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
