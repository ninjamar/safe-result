import asyncio
import traceback
from functools import wraps
from typing import Any, Awaitable, Callable, Generic, Optional, TypeVar, Union, cast

T = TypeVar("T")
E = TypeVar("E", bound=Exception)


class Result(Generic[T, E]):
    """A class that represents the result of an operation."""

    def __init__(self, value: Optional[T] = None, error: Optional[E] = None):
        self.value = value
        self.error = error
        self.traceback: Optional[str] = None

        # Capture traceback if there's an error
        if error is not None:
            self.traceback = "".join(
                traceback.format_exception(type(error), error, error.__traceback__)
            )

    def is_error(self) -> bool:
        """Check if this Result contains an error."""
        return self.error is not None

    def unwrap(self) -> T:
        """Return the value or raise the error."""
        if self.error:
            raise self.error
        return cast(T, self.value)

    def unwrap_or(self, default: T) -> T:
        """Return the value or a default if there's an error."""
        if self.error:
            return default
        return cast(T, self.value)

    def __str__(self) -> str:
        if self.is_error():
            return f"Error: {self.error}"
        return str(self.value)

    def __repr__(self) -> str:
        if self.is_error():
            return f"Result(error={self.error})"
        return f"Result(value={self.value})"

    @staticmethod
    def safe(
        func: Callable[..., Union[T, Awaitable[T]]],
    ) -> Callable[
        ..., Union["Result[T, Exception]", Awaitable["Result[T, Exception]"]]
    ]:
        """
        Decorator that wraps a function to return a Result.
        The decorated function will never raise exceptions.
        Works with both synchronous and asynchronous functions.

        Example:
            >>> @Result.safe
            ... def divide(a: int, b: int) -> float:
            ...     return a / b
            ...
            >>> result = divide(10, 0)  # Returns Result with ZeroDivisionError

            >>> @Result.safe
            ... async def async_divide(a: int, b: int) -> float:
            ...     return a / b
            ...
            >>> result = await async_divide(10, 0)  # Returns Result with ZeroDivisionError
        """
        if asyncio.iscoroutinefunction(func):

            @wraps(func)
            async def async_wrapper(
                *args: Any, **kwargs: Any
            ) -> "Result[T, Exception]":
                try:
                    value = await cast(Awaitable[T], func(*args, **kwargs))
                    return Result(value=value)
                except asyncio.CancelledError as e:
                    return Result(error=e)
                except Exception as e:
                    return Result(error=e)

            return async_wrapper
        else:

            @wraps(func)
            def sync_wrapper(*args: Any, **kwargs: Any) -> "Result[T, Exception]":
                try:
                    return Result(value=cast(T, func(*args, **kwargs)))
                except Exception as e:
                    return Result(error=e)

            return sync_wrapper
