import asyncio
from typing import List, Optional

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
        return lst[10] + "invalid"

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


def test_result_with_none_value():
    result = Result[Optional[int], Exception](value=None)
    assert not result.is_error()
    assert result.value is None
    assert result.unwrap() is None
    assert result.unwrap_or(42) is None


def test_result_with_falsy_values():
    cases = [
        Result(value=""),
        Result(value=0),
        Result(value=[]),
        Result(value={}),
        Result(value=False),
    ]

    for result in cases:
        assert not result.is_error()
        assert result.value == result.unwrap()


def test_nested_results():
    inner_success = Result(value=42)
    outer_success = Result(value=inner_success)

    inner_error = Result(error=ValueError("inner error"))
    outer_error = Result(value=inner_error)

    assert not outer_success.is_error()
    assert isinstance(outer_success.value, Result)
    assert outer_success.value.value == 42

    assert not outer_error.is_error()
    assert isinstance(outer_error.value, Result)
    assert outer_error.value.is_error()


def test_safe_decorator_with_generator():
    @Result.safe
    def generate_numbers():
        for i in range(3):
            if i == 2:
                raise ValueError("Stop at 2")
            yield i

    try:
        list(generate_numbers().unwrap())
        assert False, "Should have raised ValueError"
    except ValueError as e:
        assert str(e) == "Stop at 2"


@pytest.mark.asyncio
async def test_safe_decorator_async_cancellation():
    @Result.safe
    async def long_operation() -> str:
        try:
            await asyncio.sleep(1)
            return "completed"
        except asyncio.CancelledError:
            raise  # Re-raise to be caught by the decorator

    task = asyncio.create_task(long_operation())
    await asyncio.sleep(0.01)  # Give the task a chance to start
    task.cancel()

    result = await task
    assert result.is_error()
    assert isinstance(result.error, asyncio.CancelledError)


def test_result_type_hints():
    str_result: Result[str, Exception] = Result(value="test")
    assert isinstance(str_result.value, str)

    list_result: Result[List[int], Exception] = Result(value=[1, 2, 3])
    assert isinstance(list_result.value, list)

    optional_result: Result[Optional[int], Exception] = Result(value=None)
    assert optional_result.value is None


def test_result_with_custom_exception():
    class CustomError(Exception):
        pass

    result = Result[int, CustomError](error=CustomError("custom error"))
    assert result.is_error()
    assert isinstance(result.error, CustomError)

    with pytest.raises(CustomError):
        result.unwrap()


@pytest.mark.asyncio
async def test_safe_decorator_async_context_manager():
    class AsyncResource:
        async def __aenter__(self):
            return self

        async def __aexit__(self, exc_type, exc_val, exc_tb):
            if exc_type is not None:
                return False  # Don't suppress the error

    @Result.safe
    async def use_resource():
        async with AsyncResource():
            raise RuntimeError("Operation failed")

    result = await use_resource()
    assert result.is_error()
    assert isinstance(result.error, RuntimeError)
    assert str(result.error) == "Operation failed"


def test_result_equality():
    result1 = Result(value=42)
    result2 = Result(value=42)
    result3 = Result(value=43)
    error_result = Result(error=ValueError())

    assert result1.value == result2.value
    assert result1.value != result3.value
    assert result1.value != error_result.value
