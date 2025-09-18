"""
Web scraping tools module - compatibility layer for fetch_tools.py
This module re-exports functions from fetch_tools.py for backward compatibility.
"""

from .fetch_tools import (
    http_request,
    fetch_webpage,  # Correct function name from fetch_tools
    download_file,
    api_call,
    batch_requests,
    get_fetch_tools as get_web_scraping_tools  # Correct function name
)

# Also export as webpage for backward compatibility
webpage = fetch_webpage

# Re-export all functions for backward compatibility
__all__ = [
    'get_web_scraping_tools',
    'http_request',
    'fetch_webpage',
    'webpage',
    'download_file',
    'api_call',
    'batch_requests'
]