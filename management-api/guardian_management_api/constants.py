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

# To accommodate some backends we proactively restrict the length of non text field strings.
# This affects mostly names and display names.
STRING_MAX_LENGTH = 256

DEFAULT_BUNDLE_SERVER_BASE_DIR = "/guardian_service_dir/bundle_server"
BUNDLE_SERVER_DISABLED_SETTING_NAME = "bundle_server.disabled"
