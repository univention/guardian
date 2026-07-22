#!/usr/bin/python3
# SPDX-FileCopyrightText: 2026 Univention GmbH
# SPDX-License-Identifier: AGPL-3.0-only

from subprocess import call  # nosec B404


def postinst(ucr, changes):
    call(['/usr/bin/systemctl', 'try-restart', 'univention-guardian-server'])  # nosec B603
