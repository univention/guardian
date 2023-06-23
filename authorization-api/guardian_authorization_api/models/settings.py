# Copyright (C) 2023 Univention GmbH
#
# SPDX-License-Identifier: AGPL-3.0-only

from typing import TypeVar

SettingType = TypeVar("SettingType", bound=int | str | bool)
SETTINGS_NAME_METADATA = "guardian_authz_settings_name"
