# Copyright (C) 2023 Univention GmbH
#
# SPDX-License-Identifier: AGPL-3.0-only

import pytest_asyncio
from guardian_authorization_api.logging import configure_logger


@pytest_asyncio.fixture(autouse=True)
async def setup_logging():
    await configure_logger()
