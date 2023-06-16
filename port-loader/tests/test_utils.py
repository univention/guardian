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
    ep_mock = mocker.MagicMock(return_value={"some_string": (ep1_mock, ep2_mock)})
    mocker.patch("port_loader.utils.metadata.entry_points", ep_mock)
    load_from_entry_point(registry_mock, object, "some_string")
    assert registry_mock.register_adapter.call_args_list == [
        mocker.call(object, adapter_cls=ep1_mock.load()),
        mocker.call(object, adapter_cls=ep2_mock.load()),
    ]
