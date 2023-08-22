# Copyright (C) 2023 Univention GmbH
#
# SPDX-License-Identifier: AGPL-3.0-only

import loguru
from guardian_lib.ports import BasePort


class TestPort(BasePort):
    ...


def test_logger_property():
    port = TestPort()
    logger1 = port.logger
    logger2 = port.logger
    assert logger1 != logger2
    assert isinstance(logger1, type(loguru.logger))
