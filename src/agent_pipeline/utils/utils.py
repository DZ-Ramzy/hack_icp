"""
Simple utilities for better error handling and timeouts.
"""

import asyncio
import functools
from typing import Any, Callable, Optional


async def with_timeout(coro, timeout_seconds: int = 60, error_message: str = "Operation timed out"):
    """
    Simple timeout wrapper for async operations.
    """
    try:
        return await asyncio.wait_for(coro, timeout=timeout_seconds)
    except asyncio.TimeoutError:
        raise TimeoutError(f"{error_message} (after {timeout_seconds}s)")


def retry_on_error(max_retries: int = 3, delay_seconds: float = 1.0):
    """
    Simple retry decorator for functions that might fail.
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def wrapper(*args, **kwargs) -> Any:
            last_error = None
            
            for attempt in range(max_retries):
                try:
                    return await func(*args, **kwargs)
                except Exception as e:
                    last_error = e
                    if attempt < max_retries - 1:
                        print(f"Attempt {attempt + 1} failed for {func.__name__}: {e}")
                        await asyncio.sleep(delay_seconds * (2 ** attempt))  # Exponential backoff
                    else:
                        print(f"All {max_retries} attempts failed for {func.__name__}")
            
            raise last_error
        
        return wrapper
    return decorator


def safe_execute(default_value: Any = None, log_errors: bool = True):
    """
    Safe execution decorator that returns default value on error.
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def wrapper(*args, **kwargs) -> Any:
            try:
                return await func(*args, **kwargs)
            except Exception as e:
                if log_errors:
                    print(f"Error in {func.__name__}: {e}")
                return default_value
        
        return wrapper
    return decorator