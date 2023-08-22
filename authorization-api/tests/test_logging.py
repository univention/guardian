# Copyright (C) 2023 Univention GmbH
#
# SPDX-License-Identifier: AGPL-3.0-only

import sys

import pytest
from guardian_authorization_api.logging import configure_logger


@pytest.mark.asyncio
async def test_configure_logger(mocker):
    """
    This test checks some assumptions about the logging configuration
    """
    log_mock = mocker.MagicMock()
    mocker.patch("guardian_lib.logging.logger", log_mock)
    await configure_logger()
    # port-loader logging is enabled
    log_mock.enable.assert_called_once_with("port_loader")
    # Default handlers are removed
    log_mock.remove.assert_called_once()
    # Handler with default options added
    log_mock.add.assert_called_once_with(
        sys.stderr,
        format="<green>{time:YYYY-MM-DD HH:mm:ss.SSS ZZ}</green> | <level>{level}</level> "
        "| <level>{message}</level> | {extra}",
        serialize=False,
        level="DEBUG",
        colorize=True,
        enqueue=True,
        backtrace=False,
        diagnose=False,
    )
