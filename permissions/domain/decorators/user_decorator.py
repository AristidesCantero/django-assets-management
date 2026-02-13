import functools
from typing import Any, Callable, Optional, TypeVar, cast

T = TypeVar('T')

class ReturnEarly(Exception):
    """Exception to signal early return from parent function"""
    def __init__(self, value: Any = None):
        self.value = value
        super().__init__()

def returns_from_inner(func: Callable[..., Any]) -> Callable[..., Any]:
    """
    Decorator that makes the parent function return whatever the decorated
    inner function returns (if not None)
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        result = func(*args, **kwargs)
        if result is not None:
            raise ReturnEarly(result)
        return result
    return wrapper

def handle_early_return(func: Callable[..., Any]) -> Callable[..., Any]:
    """
    Decorator for parent functions to handle ReturnEarly exceptions
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except ReturnEarly as e:
            return e.value
    return wrapper