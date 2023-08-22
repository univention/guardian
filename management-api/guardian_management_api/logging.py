# Copyright (C) 2023 Univention GmbH
#
# SPDX-License-Identifier: AGPL-3.0-only
from functools import partial

from guardian_lib.logging import configure_logger as lib_configure_logger

setting_names = {
    "LOG_FORMAT_SETTING_NAME": "guardian.management.logging.format",
    "STRUCTURED_SETTING_NAME": "guardian.management.logging.structured",
    "LOG_LEVEL_SETTING_NAME": "guardian.management.logging.level",
    "BACKTRACE_SETTING_NAME": "guardian.management.logging.backtrace",
    "DIAGNOSE_SETTING_NAME": "guardian.management.logging.diagnose",
}

configure_logger = partial(lib_configure_logger, setting_names=setting_names)
