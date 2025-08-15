# -*- coding: utf-8 -*-
"""
Searx search tool for MCP server.

This module provides a search function that interacts with Searx instances
to perform web searches. It supports multiple Searx hosts with automatic
failover and retry logic for high availability.
"""

import json
import logging
import time
from typing import Any, Dict, List, Optional, Union

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from src.config import get_config


def create_session() -> requests.Session:
    """
    Create a requests session with retry strategy.
    
    This session includes:
    - Automatic retries for network errors
    - Connection pooling for performance
    - Proper timeout handling
    
    Returns:
        requests.Session: Configured session object.
    """
    session = requests.Session()
    
    # Configure retry strategy
    retry_strategy = Retry(
        total=3,
        backoff_factor=0.5,
        status_forcelist=[408, 429, 500, 502, 503, 504],
        allowed_methods=["GET", "POST"],
    )
    
    adapter = HTTPAdapter(
        max_retries=retry_strategy,
        pool_connections=10,
        pool_maxsize=10,
    )
    
    session.mount("http://", adapter)
    session.mount("https://", adapter)
    
    # Set default headers
    session.headers.update({
        "User-Agent": "MCP-Searx-Client/1.0",
        "Accept": "application/json",
    })
    
    return session


# Global session for connection pooling
_session: Optional[requests.Session] = None


def get_session() -> requests.Session:
    """Get or create the global session."""
    global _session
    if _session is None:
        _session = create_session()
    return _session


def search(
    query: str,
    categories: Optional[Union[str, List[str]]] = None,
    engines: Optional[Union[str, List[str]]] = None,
    language: str = "auto",
    time_range: Optional[str] = None,
    safe_search: int = 0,
    page: int = 1,
    format: str = "json"
) -> Dict[str, Any]:
    """
    Perform a search using Searx.
    
    This function sends a search query to a Searx instance and returns
    the results. It automatically handles failover between multiple
    configured Searx hosts and implements retry logic.
    
    Args:
        query: The search query string.
        categories: Search categories (e.g., "general", "images", "news").
                   Can be a single category or a list of categories.
        engines: Specific search engines to use (e.g., "google", "bing").
                Can be a single engine or a list of engines.
        language: Language preference for results (default: "auto").
                 Examples: "en-US", "zh-CN", "auto".
        time_range: Time range for results. Options:
                   - None (all time)
                   - "day" (last 24 hours)
                   - "week" (last week)
                   - "month" (last month)
                   - "year" (last year)
        safe_search: Safe search level (0=off, 1=moderate, 2=strict).
        page: Page number for pagination (starts from 1).
        format: Response format (always "json" for this tool).
    
    Returns:
        Dict containing search results with the following structure:
        {
            "query": str,              # The original query
            "results": List[Dict],     # List of search results
            "number_of_results": int,  # Total number of results
            "suggestions": List[str],  # Search suggestions
            "infoboxes": List[Dict],  # Information boxes (if any)
            "answers": List[str],     # Direct answers (if any)
            "corrections": List[str],  # Spelling corrections (if any)
        }
    
    Raises:
        ConnectionError: If all Searx hosts are unreachable.
        ValueError: If the query is empty or invalid.
        requests.RequestException: For other network-related errors.
    
    Example:
        >>> results = search("Python programming", categories="general")
        >>> for result in results["results"][:5]:
        ...     print(f"{result['title']}: {result['url']}")
    """
    # Validate input
    if not query or not query.strip():
        raise ValueError("Search query cannot be empty")
    
    # Normalize categories and engines
    if isinstance(categories, str):
        categories = [categories]
    if isinstance(engines, str):
        engines = [engines]
    
    # Load configuration
    config = get_config()
    hosts = config.searx.get_all_hosts()
    timeout = config.searx.timeout
    max_retries = config.searx.max_retries
    
    # Prepare search parameters
    params = {
        "q": query.strip(),
        "format": format,
        "language": language,
        "safesearch": safe_search,
        "pageno": page,
    }
    
    # Add optional parameters
    if categories:
        params["categories"] = ",".join(categories)
    if engines:
        params["engines"] = ",".join(engines)
    if time_range:
        params["time_range"] = time_range
    
    # Get session
    session = get_session()
    
    # Try each host with retry logic
    last_error = None
    attempts = 0
    
    for host_index, host in enumerate(hosts):
        for retry in range(max_retries):
            attempts += 1
            try:
                # Construct search URL
                search_url = f"{host}/search"
                
                logging.info(
                    "Attempting search on %s (host %d/%d, retry %d/%d)",
                    host, host_index + 1, len(hosts), retry + 1, max_retries
                )
                
                # Make the request
                response = session.get(
                    search_url,
                    params=params,
                    timeout=timeout,
                    allow_redirects=True,
                )
                
                # Check response status
                response.raise_for_status()
                
                # Parse JSON response
                data = response.json()
                
                # Validate response structure
                if not isinstance(data, dict):
                    raise ValueError(f"Invalid response format from {host}")
                
                # Add metadata to response
                data["_metadata"] = {
                    "host": host,
                    "attempts": attempts,
                    "response_time": response.elapsed.total_seconds(),
                }
                
                # Log success
                logging.info(
                    "Search successful on %s (%.2fs, %d results)",
                    host,
                    response.elapsed.total_seconds(),
                    len(data.get("results", []))
                )
                
                return data
                
            except requests.exceptions.Timeout:
                last_error = f"Timeout after {timeout}s on {host}"
                logging.warning(last_error)
                
            except requests.exceptions.ConnectionError as e:
                last_error = f"Connection error on {host}: {e}"
                logging.warning(last_error)
                
            except requests.exceptions.HTTPError as e:
                last_error = f"HTTP error on {host}: {e}"
                logging.warning(last_error)
                
                # Don't retry on client errors (4xx)
                if response.status_code < 500:
                    break
                    
            except json.JSONDecodeError as e:
                last_error = f"Invalid JSON response from {host}: {e}"
                logging.error(last_error)
                break  # Don't retry on parsing errors
                
            except Exception as e:
                last_error = f"Unexpected error on {host}: {e}"
                logging.exception(last_error)
                
            # Exponential backoff between retries
            if retry < max_retries - 1:
                wait_time = (2 ** retry) * 0.5
                logging.debug("Waiting %.1fs before retry...", wait_time)
                time.sleep(wait_time)
    
    # All attempts failed
    error_msg = f"Search failed after {attempts} attempts. Last error: {last_error}"
    logging.error(error_msg)
    raise ConnectionError(error_msg)


def search_suggestions(query: str) -> List[str]:
    """
    Get search suggestions for a query.
    
    This is a simplified wrapper around the search function that
    only returns suggestions.
    
    Args:
        query: The search query string.
    
    Returns:
        List of suggested search queries.
    
    Example:
        >>> suggestions = search_suggestions("pytho")
        >>> print(suggestions)
        ['python', 'python programming', 'python tutorial']
    """
    try:
        # Use autocomplete endpoint if available
        config = get_config()
        host = config.searx.get_random_host()
        session = get_session()
        
        autocomplete_url = f"{host}/autocompleter"
        response = session.get(
            autocomplete_url,
            params={"q": query},
            timeout=config.searx.timeout,
        )
        
        if response.status_code == 200:
            suggestions = response.json()
            if isinstance(suggestions, list):
                return suggestions[:10]  # Limit to 10 suggestions
    except Exception as e:
        logging.debug("Autocomplete failed, falling back to search: %s", e)
    
    # Fallback to regular search
    try:
        results = search(query, page=1)
        return results.get("suggestions", [])
    except Exception:
        return []


def get_supported_engines() -> List[str]:
    """
    Get a list of supported search engines from the Searx instance.
    
    Returns:
        List of available search engine names.
    
    Note:
        This requires the Searx instance to have the config endpoint enabled,
        which may not be available on all instances for security reasons.
    """
    config = get_config()
    host = config.searx.get_random_host()
    session = get_session()
    
    try:
        config_url = f"{host}/config"
        response = session.get(config_url, timeout=config.searx.timeout)
        
        if response.status_code == 200:
            data = response.json()
            engines = data.get("engines", [])
            return [engine["name"] for engine in engines if engine.get("enabled")]
    except Exception as e:
        logging.debug("Failed to get engine list: %s", e)
    
    # Return common engines as fallback
    return [
        "google", "bing", "duckduckgo", "wikipedia",
        "github", "stackoverflow", "arxiv", "pubmed"
    ]


# Export public interface
__all__ = ["search", "search_suggestions", "get_supported_engines"]