# Copyright (C) 2023 Univention GmbH
#
# SPDX-License-Identifier: AGPL-3.0-only

import inspect
from typing import Callable, ForwardRef, Type

import pytest
from port_loader import inject_port
from port_loader.errors import InjectionError
from port_loader.injection import (
    InjectionDefaultObject,
    _get_injectable_params,
    _get_injection_information,
    inject_adapter,
    inject_function,
)


@pytest.fixture
def injection_ready_registry(mock_async_registry):
    """This mock registry returns the class object passed in the request_port method."""

    async def request_port_mock(port_cls):
        return port_cls

    mock_async_registry.request_port = request_port_mock
    return mock_async_registry


@pytest.fixture
def injectable_func():
    async def test_func(a: int, b: bool = inject_port(bool), c: str = inject_port(str)):
        return a, b, c

    return test_func


@pytest.fixture
def injectable_cls():
    class TestClass:
        @staticmethod
        async def static_func(a: bool = inject_port(bool)):
            pass

        @classmethod
        async def class_func(cls, a: int = inject_port(int)):
            pass

        async def func1(self, a, b: bool):
            pass

        async def func2(self, a, b: str = inject_port(str)):
            return self, a, b

    return TestClass


def test_inject_port():
    result = inject_port(int)
    assert isinstance(result, InjectionDefaultObject)
    assert result.injection_type == int


def test_get_injectable_params():
    def test_func(
        a: int, b: str = "txt", c: int = inject_port(int), d: bool = inject_port(bool)
    ):
        pass

    assert _get_injectable_params(test_func) == {"c": int, "d": bool}


def test_get_injectable_params_no_injectables():
    def test_func(a: int, b: str, c: bool = False):
        pass

    assert _get_injectable_params(test_func) == {}


def test_get_injection_information(injectable_cls):
    assert _get_injection_information(injectable_cls) == {"func2": {"b": str}}


def test_inject_function_returns_decorator(mock_async_registry):
    """Checks that a decorator is returned, if parameter func is not supplied."""
    decorator = inject_function(mock_async_registry, params={})
    assert inspect.isfunction(decorator)
    signature = inspect.signature(decorator)
    assert len(signature.parameters) == 1
    assert signature.parameters["func"].name == "func"
    assert signature.parameters["func"].annotation == Callable


def test_inject_function_async_only(mock_async_registry):
    def test_func():
        pass

    with pytest.raises(
        InjectionError, match="Injection currently only works for async functions."
    ):
        inject_function(mock_async_registry, params={}, func=test_func)


@pytest.mark.asyncio
@pytest.mark.parametrize("params", [None, {"b": bool, "c": str}])
async def test_inject_function(
    mocker, injection_ready_registry, injectable_func, params
):
    _get_injectable_params_mock = mocker.MagicMock(return_value={"b": bool, "c": str})
    mocker.patch(
        "port_loader.injection._get_injectable_params", _get_injectable_params_mock
    )

    result = await inject_function(
        injection_ready_registry, params=params, func=injectable_func
    )(5)
    assert result == (5, bool, str)


@pytest.mark.asyncio
async def test_inject_function_override_injected(
    injection_ready_registry, injectable_func
):
    decorated_func = inject_function(
        injection_ready_registry, params={"b": bool, "c": str}, func=injectable_func
    )
    assert await decorated_func(5, c="txt") == (5, bool, "txt")


def test_inject_adapter_returns_decorator(mock_async_registry):
    """Checks that a decorator is returned, if parameter adapter_cls is not supplied."""
    decorator = inject_adapter(mock_async_registry)
    assert inspect.isfunction(decorator)
    signature = inspect.signature(decorator)
    assert len(signature.parameters) == 1
    assert signature.parameters["adapter_cls"].name == "adapter_cls"
    assert signature.parameters["adapter_cls"].annotation == Type[ForwardRef("Adapter")]


@pytest.mark.asyncio
async def test_inject_adapter(mocker, injection_ready_registry, injectable_cls):
    get_injection_info_mock = mocker.MagicMock(return_value={"func2": {"b": str}})
    mocker.patch(
        "port_loader.injection._get_injection_information", get_injection_info_mock
    )
    injected_cls = inject_adapter(injection_ready_registry, adapter_cls=injectable_cls)
    instance = injected_cls()
    assert await instance.func2(5) == (instance, 5, str)
