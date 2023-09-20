# Copyright (C) 2023 Univention GmbH
#
# SPDX-License-Identifier: AGPL-3.0-only
import os

API_PREFIX = os.environ.get("GUARDIAN__AUTHZ__API_PREFIX", "/guardian/authorization")

CORS_ALLOWED_ORIGINS = os.environ.get("GUARDIAN__AUTHZ__CORS__ALLOWED_ORIGINS")
