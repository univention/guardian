# Copyright (C) 2023 Univention GmbH
#
# SPDX-License-Identifier: AGPL-3.0-only


from guardian_management_api.ports.base import BasePort


class BaseAdapter(BasePort):
    ...


class TestBasePort:
    def test_base_port(self):
        BaseAdapter()
