# Copyright (C) 2023 Univention GmbH
#
# SPDX-License-Identifier: AGPL-3.0-only

from typing import Optional, Type

import pytest
from guardian_management_api.errors import SettingFormatError, SettingTypeError
from guardian_management_api.ports.base import BasePort
from guardian_management_api.ports.settings import SettingsPort
from port_loader import Settings


class BaseAdapter(BasePort):
    ...


class TestBasePort:
    def test_base_port(self):
        BaseAdapter()
