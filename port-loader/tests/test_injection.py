import pytest
from port_loader.errors import InjectionError
from port_loader.injection import (
    InjectionDefaultObject,
    _get_injection_information,
    inject_adapter,
    inject_function,
    inject_port,
)


class MyAdapter:
    async def my_func(self, a: int, b: str = "text", c: bool = inject_port(bool)):
        pass

    @classmethod
    async def other_func(cls, a: int = inject_port(int), b: bool = inject_port(bool)):
        pass

    @staticmethod
    async def static_func(self):
        pass


def test_inject_port():
    obj = inject_port(bool)
    assert isinstance(obj, InjectionDefaultObject)
    assert obj.injection_type == bool


def test_get_injection_information():
    injectables = _get_injection_information(MyAdapter)
    assert dict(injectables) == {"my_func": {"c": bool}}


@pytest.mark.asyncio
async def test_inject_function(mocker):
    registry_mock = mocker.AsyncMock()
    decorated = inject_function(registry_mock, {"c": bool})(MyAdapter.my_func)
    await decorated(MyAdapter(), 5)
    assert registry_mock.get_adapter.call_args_list == [
        mocker.call(bool),
    ]


def test_inject_function_only_async(mocker):
    def sync_func(a: int = inject_port(int)):
        pass

    registry_mock = mocker.AsyncMock()
    with pytest.raises(
        InjectionError, match="Injection currently only works for async functions."
    ):
        inject_function(registry_mock, {})(sync_func)


@pytest.mark.asyncio
async def test_inject_adapter(mocker):
    registry_mock = mocker.AsyncMock()
    inject_adapter(registry_mock)(MyAdapter)
    obj = MyAdapter()
    await obj.my_func(5)
    assert registry_mock.get_adapter.call_args_list == [
        mocker.call(bool),
    ]
