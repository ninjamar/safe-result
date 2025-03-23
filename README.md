# Safe Result

A Python library providing a Result type for elegant error handling, inspired by Rust's Result type.

## Installation

```bash
pip install safe-result
```

## Overview

Safe Result provides a `Result` type that represents either success (`value`) or failure (`error`). This allows for more explicit error handling without relying on exceptions, making your code more predictable and easier to reason about.

Key features:

- Type-safe result handling with generics support
- Decorator for automatically wrapping function returns in Result objects
- Support for both synchronous and asynchronous functions
- Built-in traceback capture for errors

## Usage

### Basic Usage

```python
from safe_result import Result

# Success case
success = Result(value=42)
if not success.is_error():
    print(success.value)  # 42

# Error case
error = Result(error=ValueError("something went wrong"))
if error.is_error():
    print(f"Error occurred: {error.error}")
```

### Using the Decorator

The `@Result.safe` decorator automatically wraps function returns in a Result object:

```python
from safe_result import Result

@Result.safe
def divide(a: int, b: int) -> float:
    return a / b

# Success case
result = divide(10, 2)
if not result.is_error():
    print(result.value)  # 5.0

# Error case
result = divide(10, 0)
if result.is_error():
    print(f"Error: {result.error}")  # Error: division by zero
```

### Async Functions

The decorator works with async functions too:

```python
import asyncio
from safe_result import Result

@Result.safe
async def async_operation(value: int) -> int:
    await asyncio.sleep(0.1)
    if value == 0:
        raise ValueError("Cannot process zero")
    return value * 2

async def main():
    # Success case
    result = await async_operation(5)
    print(result.unwrap())  # 10

    # Error case
    result = await async_operation(0)
    print(result.unwrap_or(42))  # 42

asyncio.run(main())
```

### Unwrapping Results

```python
from safe_result import Result

# Get value or raise the stored exception
result = Result(value="hello")
value = result.unwrap()  # "hello"

# Get value or return a default
error_result = Result(error=ValueError("oops"))
value = error_result.unwrap_or("default")  # "default"
```

## API Reference

### `Result[T, E]`

Generic class representing either success (with value of type T) or failure (with error of type E).

#### Constructor

- `Result(value=None, error=None)`: Create a new Result with either a value or an error

#### Methods

- `is_error() -> bool`: Check if the Result contains an error
- `unwrap() -> T`: Return the value or raise the stored error
- `unwrap_or(default: T) -> T`: Return the value or a default if there's an error

#### Class Methods

- `@Result.safe`: Decorator that wraps a function to return a Result

## License

MIT
