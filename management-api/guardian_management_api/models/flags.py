# Copyright (C) 2026 Univention GmbH
#
# SPDX-License-Identifier: AGPL-3.0-only

from enum import IntFlag


class Flag(IntFlag):
    NONE = 0
    IS_BUILTIN = 1 << 0
