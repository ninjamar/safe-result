import asyncio

import pytest

from safe_result import Result


def test_result_success():
    result = Result(value=42)
    assert not result.is_error()
    assert result.value == 42
    assert result.error is None
    assert result.unwrap() == 42
    assert result.unwrap_or(0) == 42


def test_result_error():
    error = ValueError("test error")
    result = Result(error=error)
    assert result.is_error()
    assert result.value is None
    assert result.error == error
    assert result.unwrap_or(42) == 42
    with pytest.raises(ValueError):
        result.unwrap()


def test_result_str_representation():
    success_result = Result(value="success")
    error_result = Result(error=ValueError("test error"))

    assert str(success_result) == "success"
    assert "Error: test error" in str(error_result)
    assert "Result(value=success)" in repr(success_result)
    assert "Result(error=" in repr(error_result)


def test_safe_decorator_sync():
    @Result.safe
    def divide(a: int, b: int) -> float:
        return a / b

    success = divide(10, 2)
    assert not success.is_error()
    assert success.value == 5.0

    error = divide(10, 0)
    assert error.is_error()
    assert isinstance(error.error, ZeroDivisionError)


@pytest.mark.asyncio
async def test_safe_decorator_async():
    @Result.safe
    async def async_divide(a: int, b: int) -> float:
        await asyncio.sleep(0.01)  # Simulate async operation
        return a / b

    success = await async_divide(10, 2)
    assert not success.is_error()
    assert success.value == 5.0

    error = await async_divide(10, 0)
    assert error.is_error()
    assert isinstance(error.error, ZeroDivisionError)


def test_result_traceback():
    try:
        raise ValueError("test error")
    except ValueError as e:
        result = Result(error=e)
        assert result.traceback is not None
        assert "ValueError: test error" in result.traceback


def test_safe_decorator_with_complex_error():
    @Result.safe
    def complex_operation(lst: list) -> int:
        return lst[10] + "invalid"  # This will raise multiple possible errors

    result = complex_operation([1, 2, 3])
    assert result.is_error()
    assert isinstance(result.error, IndexError)


def test_unwrap_or_with_different_types():
    str_result = Result[str, Exception](value="hello")
    assert str_result.unwrap_or("default") == "hello"

    error_result = Result[str, Exception](error=ValueError())
    assert error_result.unwrap_or("default") == "default"


def test_multiple_result_instances():
    r1 = Result(value=1)
    r2 = Result(value=2)
    r3 = Result(error=ValueError())

    assert r1.value != r2.value
    assert not r1.is_error() and not r2.is_error()
    assert r3.is_error()


@pytest.mark.asyncio
async def test_safe_decorator_async_exception_handling():
    @Result.safe
    async def async_fail() -> None:
        await asyncio.sleep(0.01)
        raise RuntimeError("async error")

    result = await async_fail()
    assert result.is_error()
    assert isinstance(result.error, RuntimeError)
    assert "async error" in str(result.error)
