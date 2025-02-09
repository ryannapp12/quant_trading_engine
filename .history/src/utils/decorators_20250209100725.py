# src/utils/decorators.py

import time
import functools
import logging
from src.utils.logger import setup_logger

logger = setup_logger("decorators", level=logging.INFO)

def timeit(func):
    """Decorator to measure execution time of functions."""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        elapsed = time.time() - start_time
        logger.info(f"{func.__name__} executed in {elapsed:.4f} seconds")
        return result
    return wrapper