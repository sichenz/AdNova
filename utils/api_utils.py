"""
Utilities for API interactions.
This module handles API client initialization and error handling.
"""
import sys
import time
from typing import Optional, Dict, Any

from openai import OpenAI, APIError, RateLimitError
from config.settings import OPENAI_API_KEY

def get_openai_client(api_key: Optional[str] = None) -> OpenAI:
    """
    Get an initialized OpenAI API client.
    
    Args:
        api_key: Optional API key (uses the one from settings if not provided)
        
    Returns:
        Initialized OpenAI client
    """
    # Use the provided API key or the one from settings
    key = api_key or OPENAI_API_KEY
    
    if not key:
        print("Error: OpenAI API key not found. Please set it in your .env file or provide it directly.")
        sys.exit(1)
    
    return OpenAI(api_key=key)

def retry_with_exponential_backoff(
    func,
    initial_delay: float = 1,
    exponential_base: float = 2,
    jitter: bool = True,
    max_retries: int = 5,
    errors: tuple = (RateLimitError,),
):
    """
    Retry a function with exponential backoff.
    
    Args:
        func: The function to execute
        initial_delay: Initial delay between retries in seconds
        exponential_base: Base for exponential backoff
        jitter: Whether to add random jitter to delay
        max_retries: Maximum number of retries
        errors: Tuple of exceptions to catch and retry on
        
    Returns:
        Result of the function
    """
    import random
    import logging
    
    def wrapper(*args, **kwargs):
        # Initialize variables
        num_retries = 0
        delay = initial_delay
        
        # Loop until a successful response or max_retries is hit
        while True:
            try:
                return func(*args, **kwargs)
            
            # Retry on specified errors
            except errors as e:
                # Increment retries
                num_retries += 1
                
                # Check if max retries has been reached
                if num_retries > max_retries:
                    raise Exception(f"Maximum number of retries ({max_retries}) exceeded.")
                
                # Increment the delay
                delay *= exponential_base * (1 + jitter * random.random())
                
                # Log the error and retry attempt
                logging.warning(f"Request failed with error: {e}. Retrying in {delay:.2f} seconds...")
                
                # Sleep for the delay
                time.sleep(delay)
    
    return wrapper

def safe_api_call(func, *args, **kwargs):
    """
    Make a safe API call with retry logic and error handling.
    
    Args:
        func: The API function to call
        *args: Arguments for the function
        **kwargs: Keyword arguments for the function
        
    Returns:
        Result of the API call or None if it fails
    """
    retryable_func = retry_with_exponential_backoff(func)
    
    try:
        return retryable_func(*args, **kwargs)
    except Exception as e:
        print(f"API call failed after multiple retries: {str(e)}")
        return None