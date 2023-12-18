# Copyright (C) 2023 Univention GmbH
#
# SPDX-License-Identifier: AGPL-3.0-only

import os
from importlib import reload

import guardian_management_api.constants
import pytest


class TestConstants:
    def test_undefined_base_url(self):
        old_base_url = os.environ.pop("GUARDIAN__MANAGEMENT__BASE_URL", None)
        with pytest.raises(RuntimeError):
            reload(guardian_management_api.constants)
        if old_base_url:
            os.environ["GUARDIAN__MANAGEMENT__BASE_URL"] = old_base_url
