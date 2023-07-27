# Copyright (C) 2023 Univention GmbH
#
# SPDX-License-Identifier: AGPL-3.0-only

import os
from urllib.parse import urljoin

API_PREFIX = os.environ.get("GUARDIAN__MANAGEMENT__API_PREFIX", "/guardian/management")
BASE_URL = os.environ.get("GUARDIAN__MANAGEMENT__BASE_URL")
if not BASE_URL:
    raise RuntimeError("GUARDIAN__MANAGEMENT__BASE_URL is not set")
COMPLETE_URL = urljoin(BASE_URL, API_PREFIX)
