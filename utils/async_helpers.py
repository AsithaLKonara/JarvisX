"""
Async Utilities for CLI Commands
Provides async support for long-running operations
"""

import asyncio
from typing import Callable, Any, Coroutine
from functools import wraps
import concurrent.futures
from pathlib import Path


def run_async(coro: Coroutine) -> Any:
    """
    Run async coroutine in sync context
    
    Args:
        coro: Async coroutine to run
        
    Returns:
        Result of coroutine
    """
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    
    return loop.run_until_complete(coro)


def async_command(func: Callable) -> Callable:
    """
    Decorator to make CLI command async-capable
    
    Args:
        func: Function to wrap
        
    Returns:
        Wrapped function
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        # Check if function is async
        if asyncio.iscoroutinefunction(func):
            return run_async(func(*args, **kwargs))
        else:
            return func(*args, **kwargs)
    return wrapper


def run_in_thread(func: Callable, *args, **kwargs) -> Any:
    """
    Run function in separate thread
    
    Args:
        func: Function to run
        *args: Function arguments
        **kwargs: Function keyword arguments
        
    Returns:
        Function result
    """
    with concurrent.futures.ThreadPoolExecutor() as executor:
        future = executor.submit(func, *args, **kwargs)
        return future.result()


async def run_async_operation(operation: Callable, *args, **kwargs) -> Any:
    """
    Run operation asynchronously
    
    Args:
        operation: Operation to run
        *args: Operation arguments
        **kwargs: Operation keyword arguments
        
    Returns:
        Operation result
    """
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, lambda: operation(*args, **kwargs))


class AsyncBatchProcessor:
    """Process multiple operations in parallel"""
    
    def __init__(self, max_workers: int = 5):
        """
        Initialize batch processor
        
        Args:
            max_workers: Maximum parallel workers
        """
        self.max_workers = max_workers
    
    async def process_batch(self, operations: list[Callable], *args, **kwargs) -> list[Any]:
        """
        Process batch of operations in parallel
        
        Args:
            operations: List of operations to run
            *args: Common arguments for all operations
            **kwargs: Common keyword arguments
            
        Returns:
            List of results
        """
        tasks = [
            run_async_operation(op, *args, **kwargs)
            for op in operations
        ]
        return await asyncio.gather(*tasks)
    
    def process_sync(self, operations: list[Callable], *args, **kwargs) -> list[Any]:
        """
        Process batch synchronously (for non-async contexts)
        
        Args:
            operations: List of operations to run
            *args: Common arguments for all operations
            **kwargs: Common keyword arguments
            
        Returns:
            List of results
        """
        return run_async(self.process_batch(operations, *args, **kwargs))

