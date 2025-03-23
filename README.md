# Safe Result

A Python library providing a Result type for elegant error handling, inspired by Rust's Result type.

## Installation

```bash
uv pip install "git+https://github.com/overflowy/safe-result"
```

## Overview

Safe Result provides a `Result` type that represents either success (`value`) or failure (`error`). This allows for more explicit error handling without relying on exceptions, making your code more predictable and easier to reason about.

Key features:

- Type-safe result handling with generics support
- Decorators for automatically wrapping function returns in Result objects
- Support for both synchronous and asynchronous functions
- Built-in traceback capture for errors

## Advantages Over Traditional Try/Catch

Using `safe_result` offers several benefits over traditional try/catch exception handling:

1. **Explicitness**: Forces error handling to be explicit rather than implicit, preventing overlooked exceptions
2. **Type Safety**: Leverages Python's type system to ensure proper error handling at development time
3. **Function Composition**: Makes it easier to compose functions that might fail without nested try/except blocks
4. **Predictable Control Flow**: Code execution becomes more predictable without exception-based control flow jumps
5. **Error Propagation**: Simplifies error propagation through call stacks without complex exception handling chains
6. **Traceback Preservation**: Automatically captures and preserves tracebacks while allowing normal control flow
7. **Separation of Concerns**: Cleanly separates error handling logic from business logic
8. **API Boundaries**: Provides a clear pattern for handling errors across API boundaries
9. **Testing**: Makes testing error conditions more straightforward since errors are just values

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

The `@Result.safe_async` decorator automatically wraps async functions in a Result object:

```python
import asyncio
from safe_result import Result

@Result.safe_async
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

## License

MIT
