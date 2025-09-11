"""
Secure logging utilities to prevent log injection attacks.

This module provides utilities to sanitize user input before logging,
preventing log injection vulnerabilities (CWE-117).
"""

import re
from typing import Any


def sanitize_for_log(value: Any) -> str:
    """
    Sanitize a value for safe logging by removing/replacing dangerous characters.
    
    This prevents log injection attacks by:
    1. Converting the value to string
    2. Removing carriage returns and newlines
    3. Limiting length to prevent log flooding
    4. Replacing control characters
    
    Args:
        value: The value to sanitize (can be any type)
        
    Returns:
        str: Sanitized string safe for logging
    """
    if value is None:
        return "None"
    
    # Convert to string
    str_value = str(value)
    
    # Remove carriage returns and newlines to prevent log forgery
    str_value = str_value.replace('\r\n', ' ').replace('\r', ' ').replace('\n', ' ')
    
    # Remove other control characters (except space and tab)
    str_value = re.sub(r'[\x00-\x08\x0B-\x0C\x0E-\x1F\x7F]', '', str_value)
    
    # Limit length to prevent log flooding (truncate if too long)
    max_length = 200
    if len(str_value) > max_length:
        str_value = str_value[:max_length - 3] + "..."
    
    return str_value


def secure_log_format(template: str, **kwargs) -> str:
    """
    Format a log message with sanitized values.
    
    Args:
        template: Log message template with {} placeholders
        **kwargs: Values to substitute in the template
        
    Returns:
        str: Formatted log message with sanitized values
        
    Example:
        secure_log_format("User '{user}' performed action '{action}'", 
                         user=user_input, action=action_input)
    """
    sanitized_kwargs = {key: sanitize_for_log(value) for key, value in kwargs.items()}
    return template.format(**sanitized_kwargs)


def secure_log_key_value(key: str, value: Any = None) -> str:
    """
    Create a secure log message for key-value pairs.
    
    Args:
        key: The key (e.g., cache key, file path)
        value: Optional value to include
        
    Returns:
        str: Sanitized log message
    """
    sanitized_key = sanitize_for_log(key)
    if value is not None:
        sanitized_value = sanitize_for_log(value)
        return f"key='{sanitized_key}', value='{sanitized_value}'"
    return f"key='{sanitized_key}'"