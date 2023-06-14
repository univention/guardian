import pytest
from port_loader import AsyncAdapterRegistry, get_fqcn, load_from_entry_point
from port_loader.utils import is_cached


class DummyPort:
    ...


@is_cached
class DummyAdapter(DummyPort):
    ...


@pytest.mark.parametrize(
    "cls,expected",
    [
        (int, "builtins.int"),
        (AsyncAdapterRegistry, "port_loader.registries.AsyncAdapterRegistry"),
    ],
)
def test_get_fqcn(cls, expected):
    assert get_fqcn(cls) == expected


def test_load_from_entry_point(async_port_loader, mocker):
    async_port_loader.register_port(DummyPort)
    ep_mock = mocker.MagicMock()
    ep_mock.name = "my_adapter"
    ep_mock.load = mocker.MagicMock(return_value=DummyAdapter)
    ep_load_mock = mocker.MagicMock(return_value={"some_ep": (ep_mock,)})
    mocker.patch("port_loader.utils.metadata.entry_points", ep_load_mock)
    load_from_entry_point(async_port_loader, DummyPort, "some_ep")
    adapter_config = async_port_loader._adapter_configs[get_fqcn(DummyPort)][
        get_fqcn(DummyAdapter)
    ]
    assert adapter_config.name == "my_adapter"
    assert adapter_config.adapter_cls == DummyAdapter
