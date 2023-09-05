# Copyright (C) 2023 Univention GmbH
#
# SPDX-License-Identifier: AGPL-3.0-only

import pytest
from guardian_management_api.models.routers.capability import (
    check_permissions_in_namespace,
)


def test_check_permissions_in_namespace_raises():
    values = {
        "app_name": "app",
        "namespace_name": "namespace",
        "data": {"permissions": [{"app_name": "app", "namespace_name": "ns"}]},
    }
    with pytest.raises(
        ValueError,
        match="The request contains permissions, which are in a different namespace than the "
        "capability itself.",
    ):
        check_permissions_in_namespace(None, values)


def test_check_permissions_in_namespace():
    values = {
        "app_name": "app",
        "namespace_name": "namespace",
        "data": {"permissions": [{"app_name": "app", "namespace_name": "namespace"}]},
    }
    assert check_permissions_in_namespace(None, values) == values
