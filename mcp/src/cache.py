# -*- coding: utf-8 -*-
"""
@author: l-k
@time: 2025/08/19
@description: DuckDB-based caching implementation.
"""

import pickle
import threading
from datetime import datetime, timedelta, timezone

import duckdb


class DuckDBCache:
    """
    A thread-safe caching class using DuckDB as the backend.

    This cache stores key-value pairs with a specified time-to-live (TTL).
    Values are serialized using pickle, allowing any picklable Python object
    to be cached. All database operations are protected by a lock to ensure
    thread safety.
    """

    _CREATE_TABLE_SQL = """
    CREATE TABLE IF NOT EXISTS cache (
        key VARCHAR PRIMARY KEY,
        value BLOB,
        expires_at TIMESTAMP
    );
    """

    def __init__(self, db_path: str = 'cache.db'):
        """
        Initializes the DuckDB connection and creates the cache table if it doesn't exist.

        Args:
            db_path (str): The file path for the DuckDB database.
        """
        self.db_path = db_path
        self._lock = threading.Lock()
        with self._get_connection() as conn:
            conn.execute(self._CREATE_TABLE_SQL)

    def _get_connection(self):
        """Returns a new connection to the DuckDB database."""
        return duckdb.connect(database=self.db_path, read_only=False)

    def get(self, key: str):
        """
        Retrieves a value from the cache by its key.

        Returns None if the key does not exist or the item has expired.

        Args:
            key (str): The key of the item to retrieve.

        Returns:
            The deserialized value, or None if not found or expired.
        """
        with self._lock:
            with self._get_connection() as conn:
                result = conn.execute(
                    "SELECT value, expires_at FROM cache WHERE key = ?", (key,)
                ).fetchone()

            if result:
                value_blob, expires_at = result
                if expires_at > datetime.now(timezone.utc).replace(tzinfo=None):
                    return pickle.loads(value_blob)
                else:
                    # Item has expired, delete it
                    self.delete(key)
        return None

    def set(self, key: str, value, ttl_seconds: int = 3600):
        """
        Sets a key-value pair in the cache with a TTL.

        If the key already exists, its value and expiration time will be updated.

        Args:
            key (str): The key for the item.
            value: The value to be cached. Must be picklable.
            ttl_seconds (int): Time-to-live in seconds. Defaults to 3600 (1 hour).
        """
        expires_at = datetime.now(timezone.utc).replace(tzinfo=None) + timedelta(seconds=ttl_seconds)
        serialized_value = pickle.dumps(value)

        with self._lock:
            with self._get_connection() as conn:
                conn.execute(
                    "INSERT OR REPLACE INTO cache (key, value, expires_at) VALUES (?, ?, ?)",
                    (key, serialized_value, expires_at),
                )

    def delete(self, key: str):
        """
        Deletes an item from the cache by its key.

        Args:
            key (str): The key of the item to delete.
        """
        with self._lock:
            with self._get_connection() as conn:
                conn.execute("DELETE FROM cache WHERE key = ?", (key,))

    def clear(self):
        """
        Clears all items from the cache.
        """
        with self._lock:
            with self._get_connection() as conn:
                conn.execute("DELETE FROM cache")
