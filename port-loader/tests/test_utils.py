# Copyright (C) 2023 Univention GmbH
#
# SPDX-License-Identifier: AGPL-3.0-only

import pytest
from port_loader import AsyncAdapterRegistry, get_fqcn, load_from_entry_point


@pytest.mark.parametrize(
    "subject,expected",
    [
        (int, "builtins.int"),
        (AsyncAdapterRegistry, "port_loader.registries.AsyncAdapterRegistry"),
    ],
)
def test_get_fqcn(subject, expected):
    assert get_fqcn(subject) == expected


def test_load_from_entry_point(mocker):
    registry_mock = mocker.MagicMock()
    ep1_mock = mocker.MagicMock()
    ep2_mock = mocker.MagicMock()
    ep_mock = mocker.MagicMock(return_value=(ep1_mock, ep2_mock))
    mocker.patch("port_loader.utils.metadata.entry_points", ep_mock)
    load_from_entry_point(registry_mock, object, "some_string")
    ep_mock.assert_called_once_with(group="some_string")
    assert registry_mock.register_adapter.call_args_list == [
        mocker.call(object, adapter_cls=ep1_mock.load()),
        mocker.call(object, adapter_cls=ep2_mock.load()),
    ]
