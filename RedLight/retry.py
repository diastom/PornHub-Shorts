"""Smart retry with exponential backoff for RedLight DL."""

import time
import random
import functools
from typing import Callable, Tuple, Type, Optional


class RetryError(Exception):
    """Raised when all retries are exhausted."""
    def __init__(self, message: str, last_exception: Optional[Exception] = None):
        super().__init__(message)
        self.last_exception = last_exception


def smart_retry(
    max_attempts: int = 3,
    base_delay: float = 1.0,
    max_delay: float = 60.0,
    exponential_base: float = 2.0,
    jitter: bool = True,
    exceptions: Tuple[Type[Exception], ...] = (Exception,),
    on_retry: Optional[Callable] = None
):
    """Decorator for retrying with exponential backoff."""
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            last_exception = None
            
            for attempt in range(1, max_attempts + 1):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    last_exception = e
                    
                    if attempt == max_attempts:
                        raise RetryError(f"Failed after {max_attempts} attempts", e) from e
                    
                    delay = min(base_delay * (exponential_base ** (attempt - 1)), max_delay)
                    if jitter:
                        delay = delay * (0.5 + random.random())
                    
                    if on_retry:
                        on_retry(attempt, delay, e)
                    
                    time.sleep(delay)
            
            raise RetryError(f"Failed after {max_attempts} attempts", last_exception)
        
        return wrapper
    return decorator


class RetryHandler:
    """Context manager for retry operations."""
    
    def __init__(
        self,
        max_attempts: int = 3,
        base_delay: float = 1.0,
        max_delay: float = 60.0,
        exponential_base: float = 2.0,
        jitter: bool = True
    ):
        self.max_attempts = max_attempts
        self.base_delay = base_delay
        self.max_delay = max_delay
        self.exponential_base = exponential_base
        self.jitter = jitter
        self.attempt = 0
        self.last_exception: Optional[Exception] = None
    
    def __enter__(self):
        self.attempt = 0
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        return False
    
    def should_retry(self, exception: Optional[Exception] = None) -> bool:
        self.attempt += 1
        self.last_exception = exception
        
        if self.attempt >= self.max_attempts:
            return False
        return True
    
    def wait(self):
        delay = min(self.base_delay * (self.exponential_base ** (self.attempt - 1)), self.max_delay)
        if self.jitter:
            delay = delay * (0.5 + random.random())
        time.sleep(delay)
    
    def execute(self, func: Callable, *args, **kwargs):
        while True:
            try:
                self.attempt += 1
                return func(*args, **kwargs)
            except Exception as e:
                self.last_exception = e
                if self.attempt >= self.max_attempts:
                    raise RetryError(f"Failed after {self.max_attempts} attempts", e) from e
                self.wait()


def retry_with_backoff(
    func: Callable,
    max_attempts: int = 3,
    base_delay: float = 1.0,
    exceptions: Tuple[Type[Exception], ...] = (Exception,)
):
    """Simple function for single-use retry."""
    handler = RetryHandler(max_attempts=max_attempts, base_delay=base_delay)
    
    while True:
        try:
            handler.attempt += 1
            return func()
        except exceptions as e:
            handler.last_exception = e
            if handler.attempt >= max_attempts:
                raise RetryError(f"Failed after {max_attempts} attempts", e) from e
            handler.wait()
