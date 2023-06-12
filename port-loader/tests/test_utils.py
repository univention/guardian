import pytest
from port_loader import AsyncAdapterRegistry, get_fqcn, load_from_entry_point
from port_loader.errors import PortInjectionError
from port_loader.utils import inject_port, injected_port, is_cached


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


@pytest.mark.asyncio
async def test_inject_port(async_port_loader):
    async_port_loader.register_port(DummyPort)
    async_port_loader.register_adapter(DummyPort, set_adapter=True)(DummyAdapter)

    class MyPort:
        async def return_port_list(
            self, number: int, dummy_port: DummyPort = injected_port(DummyPort)
        ) -> list[DummyPort]:
            raise NotImplementedError

    class MyAdapter(MyPort):
        @inject_port(dummy_port=DummyPort)
        async def return_port_list(
            self, number: int, dummy_port: DummyPort = injected_port(DummyPort)
        ) -> list[DummyPort]:
            return [dummy_port] * number

    async_port_loader.register_port(MyPort)
    async_port_loader.register_adapter(MyPort, set_adapter=True)(MyAdapter)
    dummy_adapter = await async_port_loader.get_adapter(DummyPort)
    my_port = await async_port_loader.get_adapter(MyPort)
    assert await my_port.return_port_list(5) == [dummy_adapter] * 5


@pytest.mark.asyncio
async def test_inject_port_missing_(async_port_loader):
    async def test(self):
        pass

    decorated = inject_port(dummy_port=DummyPort)(test)
    with pytest.raises(
        PortInjectionError, match="Error during port injection in 'builtins.object'."
    ):
        await decorated(object())


def test_inject_port_async_only(async_port_loader):
    def test():
        pass

    with pytest.raises(
        PortInjectionError,
        match="Currently the port injection works for async methods only.",
    ):
        inject_port(dummy_port=DummyPort)(test)
