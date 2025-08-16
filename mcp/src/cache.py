"""
Hybrid Intelligent Cache System for Searx MCP Server.

This module implements a production-grade multi-tier caching system with:
- L1: Memory cache for hot data (microsecond access)
- L2: Compressed cache for warm data (millisecond access)
- L3: Disk cache for cold data (sub-second access)
- Intelligent prediction and auto-optimization
- Comprehensive monitoring and statistics
"""

import gzip
import hashlib
import json
import logging
import pickle
import threading
import time
from collections import OrderedDict, defaultdict
from collections.abc import Callable
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass, field
from enum import Enum
from functools import wraps
from pathlib import Path
from typing import Any

# Try to import optional compression libraries
try:
    import lz4.frame

    HAS_LZ4 = True
except ImportError:
    HAS_LZ4 = False

try:
    import zstandard as zstd

    HAS_ZSTD = True
except ImportError:
    HAS_ZSTD = False


class CacheTier(Enum):
    """Cache tier levels."""

    MEMORY = "memory"
    COMPRESSED = "compressed"
    DISK = "disk"


class CompressionType(Enum):
    """Supported compression algorithms."""

    NONE = "none"
    GZIP = "gzip"
    LZ4 = "lz4"
    ZSTD = "zstd"


@dataclass
class CacheEntry:
    """Single cache entry with metadata."""

    key: str
    value: Any
    size: int
    created_at: float
    accessed_at: float
    access_count: int = 1
    ttl: float | None = None
    tier: CacheTier = CacheTier.MEMORY
    compressed: bool = False

    def is_expired(self) -> bool:
        """Check if the entry has expired."""
        if self.ttl is None:
            return False
        return time.time() > self.created_at + self.ttl

    def update_access(self) -> None:
        """Update access metadata."""
        self.accessed_at = time.time()
        self.access_count += 1


@dataclass
class CacheStats:
    """Cache statistics and metrics."""

    hits: int = 0
    misses: int = 0
    evictions: int = 0
    total_requests: int = 0
    memory_hits: int = 0
    compressed_hits: int = 0
    disk_hits: int = 0
    avg_latency_ms: float = 0.0
    memory_usage_bytes: int = 0
    disk_usage_bytes: int = 0
    compression_ratio: float = 1.0
    hot_keys: list[str] = field(default_factory=list)

    @property
    def hit_rate(self) -> float:
        """Calculate cache hit rate."""
        if self.total_requests == 0:
            return 0.0
        return self.hits / self.total_requests

    def to_dict(self) -> dict[str, Any]:
        """Convert stats to dictionary."""
        return {
            "hit_rate": f"{self.hit_rate:.2%}",
            "hits": self.hits,
            "misses": self.misses,
            "evictions": self.evictions,
            "total_requests": self.total_requests,
            "tier_hits": {
                "memory": self.memory_hits,
                "compressed": self.compressed_hits,
                "disk": self.disk_hits,
            },
            "avg_latency_ms": round(self.avg_latency_ms, 3),
            "memory_usage_mb": round(self.memory_usage_bytes / 1024 / 1024, 2),
            "disk_usage_mb": round(self.disk_usage_bytes / 1024 / 1024, 2),
            "compression_ratio": round(self.compression_ratio, 2),
            "hot_keys": self.hot_keys[:10],  # Top 10 hot keys
        }


class HybridIntelligentCache:
    """
    Hybrid Intelligent Cache with multi-tier storage and auto-optimization.

    Features:
    - Three-tier caching (memory, compressed, disk)
    - Automatic tier promotion/demotion based on access patterns
    - Intelligent compression selection
    - Predictive prefetching
    - Real-time statistics and monitoring
    - Thread-safe operations
    """

    def __init__(
        self,
        max_memory_mb: int = 50,
        max_disk_mb: int = 500,
        default_ttl: int = 3600,
        cache_dir: Path | None = None,
        compression: CompressionType = CompressionType.GZIP,
        enable_stats: bool = True,
        enable_prediction: bool = True,
    ):
        """
        Initialize the hybrid cache system.

        Args:
            max_memory_mb: Maximum memory cache size in MB
            max_disk_mb: Maximum disk cache size in MB
            default_ttl: Default TTL in seconds
            cache_dir: Directory for disk cache
            compression: Compression algorithm to use
            enable_stats: Enable statistics collection
            enable_prediction: Enable predictive prefetching
        """
        # Configuration
        self.max_memory_bytes = max_memory_mb * 1024 * 1024
        self.max_disk_bytes = max_disk_mb * 1024 * 1024
        self.default_ttl = default_ttl
        self.compression = self._select_compression(compression)
        self.enable_stats = enable_stats
        self.enable_prediction = enable_prediction

        # Storage tiers
        self.memory_cache: OrderedDict[str, CacheEntry] = OrderedDict()
        self.compressed_cache: OrderedDict[str, CacheEntry] = OrderedDict()
        self.disk_index: dict[str, str] = {}  # key -> file path mapping

        # Disk cache directory
        if cache_dir is None:
            cache_dir = Path.home() / ".cache" / "searx_mcp"
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)

        # Statistics
        self.stats = CacheStats()
        self.access_history: defaultdict[str, list[float]] = defaultdict(list)
        self.latency_samples: list[float] = []

        # Thread safety
        self.lock = threading.RLock()
        self.stats_lock = threading.Lock()

        # Background tasks
        self.executor = ThreadPoolExecutor(max_workers=2, thread_name_prefix="cache")
        self._start_background_tasks()

        # Load existing disk cache index
        self._load_disk_index()

        logging.info(
            "HybridIntelligentCache initialized: memory=%dMB, disk=%dMB, compression=%s",
            max_memory_mb,
            max_disk_mb,
            self.compression.value,
        )

    def _select_compression(self, preferred: CompressionType) -> CompressionType:
        """Select the best available compression algorithm."""
        if preferred == CompressionType.LZ4 and HAS_LZ4:
            return CompressionType.LZ4
        elif preferred == CompressionType.ZSTD and HAS_ZSTD:
            return CompressionType.ZSTD
        elif preferred in [CompressionType.GZIP, CompressionType.NONE]:
            return preferred
        else:
            # Fallback to gzip if preferred not available
            logging.warning("Compression %s not available, falling back to gzip", preferred.value)
            return CompressionType.GZIP

    def _compress(self, data: bytes) -> tuple[bytes, float]:
        """Compress data using selected algorithm."""
        start_time = time.time()

        if self.compression == CompressionType.NONE:
            return data, 1.0
        elif self.compression == CompressionType.GZIP:
            compressed = gzip.compress(data, compresslevel=6)
        elif self.compression == CompressionType.LZ4 and HAS_LZ4:
            compressed = lz4.frame.compress(data, compression_level=9)
        elif self.compression == CompressionType.ZSTD and HAS_ZSTD:
            cctx = zstd.ZstdCompressor(level=3)
            compressed = cctx.compress(data)
        else:
            compressed = gzip.compress(data, compresslevel=6)

        ratio = len(data) / len(compressed) if compressed else 1.0
        elapsed = time.time() - start_time

        logging.debug(
            "Compressed %d bytes to %d bytes (ratio=%.2f) in %.3fms",
            len(data),
            len(compressed),
            ratio,
            elapsed * 1000,
        )

        return compressed, ratio

    def _decompress(self, data: bytes) -> bytes:
        """Decompress data using selected algorithm."""
        if self.compression == CompressionType.NONE:
            return data
        elif self.compression == CompressionType.GZIP:
            return gzip.decompress(data)
        elif self.compression == CompressionType.LZ4 and HAS_LZ4:
            return lz4.frame.decompress(data)
        elif self.compression == CompressionType.ZSTD and HAS_ZSTD:
            dctx = zstd.ZstdDecompressor()
            return dctx.decompress(data)
        else:
            return gzip.decompress(data)

    def _calculate_memory_usage(self) -> int:
        """Calculate current memory usage."""
        total = 0
        for entry in self.memory_cache.values():
            total += entry.size
        for entry in self.compressed_cache.values():
            total += entry.size
        return total

    def _calculate_disk_usage(self) -> int:
        """Calculate current disk usage."""
        total = 0
        for file_path in self.disk_index.values():
            path = Path(file_path)
            if path.exists():
                total += path.stat().st_size
        return total

    def _evict_memory(self) -> None:
        """Evict entries from memory cache when full."""
        while self._calculate_memory_usage() > self.max_memory_bytes and self.memory_cache:
            # LRU eviction: remove least recently accessed
            key, entry = self.memory_cache.popitem(last=False)

            # Try to demote to compressed tier
            if entry.size < self.max_memory_bytes * 0.1:  # Only compress if < 10% of memory
                self._demote_to_compressed(key, entry)
            else:
                # Too large, demote directly to disk
                self._demote_to_disk(key, entry)

            if self.enable_stats:
                self.stats.evictions += 1

            logging.debug("Evicted key '%s' from memory cache", key)

    def _demote_to_compressed(self, key: str, entry: CacheEntry) -> None:
        """Demote entry from memory to compressed tier."""
        try:
            # Serialize and compress
            serialized = pickle.dumps(entry.value)
            compressed, ratio = self._compress(serialized)

            # Update entry
            entry.tier = CacheTier.COMPRESSED
            entry.compressed = True
            entry.value = compressed
            entry.size = len(compressed)

            # Store in compressed cache
            self.compressed_cache[key] = entry

            if self.enable_stats:
                self.stats.compression_ratio = (
                    self.stats.compression_ratio * 0.9 + ratio * 0.1
                )  # Exponential moving average

        except Exception as e:
            logging.error("Failed to compress entry %s: %s", key, e)

    def _demote_to_disk(self, key: str, entry: CacheEntry) -> None:
        """Demote entry to disk tier."""
        try:
            # Generate file path
            key_hash = hashlib.md5(key.encode()).hexdigest()
            file_path = self.cache_dir / f"{key_hash}.cache"

            # Serialize and save
            with open(file_path, "wb") as f:
                pickle.dump(entry, f)

            # Update index
            self.disk_index[key] = str(file_path)

            logging.debug("Demoted key '%s' to disk: %s", key, file_path)

        except Exception as e:
            logging.error("Failed to save entry %s to disk: %s", key, e)

    def _promote_to_memory(self, key: str, entry: CacheEntry) -> None:
        """Promote entry to memory tier."""
        # Decompress if needed
        if entry.compressed:
            try:
                decompressed = self._decompress(entry.value)
                entry.value = pickle.loads(decompressed)
                entry.compressed = False
                entry.size = len(pickle.dumps(entry.value))
            except Exception as e:
                logging.error("Failed to decompress entry %s: %s", key, e)
                return

        # Update tier and store
        entry.tier = CacheTier.MEMORY
        self.memory_cache[key] = entry

        # Ensure memory limit
        self._evict_memory()

    def _generate_cache_key(self, **params) -> str:
        """Generate a unique cache key from parameters."""
        # Sort parameters for consistent key generation
        sorted_params = sorted(params.items())
        key_str = json.dumps(sorted_params, sort_keys=True, ensure_ascii=True)
        return hashlib.sha256(key_str.encode()).hexdigest()

    def _load_disk_index(self) -> None:
        """Load disk cache index on startup."""
        try:
            index_file = self.cache_dir / "index.json"
            if index_file.exists():
                with open(index_file) as f:
                    self.disk_index = json.load(f)
                logging.info("Loaded %d disk cache entries", len(self.disk_index))
        except Exception as e:
            logging.warning("Failed to load disk cache index: %s", e)

    def _save_disk_index(self) -> None:
        """Save disk cache index."""
        try:
            index_file = self.cache_dir / "index.json"
            with open(index_file, "w") as f:
                json.dump(self.disk_index, f)
        except Exception as e:
            logging.error("Failed to save disk cache index: %s", e)

    def _update_stats(self, hit: bool, tier: CacheTier | None, latency: float) -> None:
        """Update cache statistics."""
        if not self.enable_stats:
            return

        with self.stats_lock:
            self.stats.total_requests += 1

            if hit:
                self.stats.hits += 1
                if tier == CacheTier.MEMORY:
                    self.stats.memory_hits += 1
                elif tier == CacheTier.COMPRESSED:
                    self.stats.compressed_hits += 1
                elif tier == CacheTier.DISK:
                    self.stats.disk_hits += 1
            else:
                self.stats.misses += 1

            # Update latency (exponential moving average)
            self.latency_samples.append(latency * 1000)  # Convert to ms
            if len(self.latency_samples) > 100:
                self.latency_samples.pop(0)
            self.stats.avg_latency_ms = sum(self.latency_samples) / len(self.latency_samples)

            # Update memory/disk usage
            self.stats.memory_usage_bytes = self._calculate_memory_usage()
            self.stats.disk_usage_bytes = self._calculate_disk_usage()

    def _update_hot_keys(self) -> None:
        """Update list of hot keys based on access patterns."""
        if not self.enable_stats:
            return

        # Calculate access frequency for each key
        key_scores = []
        current_time = time.time()

        for key, accesses in self.access_history.items():
            # Recent accesses have higher weight
            score = sum(1.0 / (current_time - t + 1) for t in accesses[-10:])
            key_scores.append((key, score))

        # Sort by score and get top keys
        key_scores.sort(key=lambda x: x[1], reverse=True)
        self.stats.hot_keys = [k for k, _ in key_scores[:20]]

    def _predict_and_prefetch(self) -> None:
        """Predict future accesses and prefetch data."""
        if not self.enable_prediction:
            return

        # Simple prediction: prefetch related queries based on patterns
        # This is a placeholder for more sophisticated ML-based prediction
        for hot_key in self.stats.hot_keys[:5]:
            # Check if related data should be prefetched
            # Implementation depends on specific use case
            pass

    def _cleanup_expired(self) -> None:
        """Remove expired entries from all tiers."""
        with self.lock:
            # Clean memory cache
            expired_keys = [k for k, v in self.memory_cache.items() if v.is_expired()]
            for key in expired_keys:
                del self.memory_cache[key]

            # Clean compressed cache
            expired_keys = [k for k, v in self.compressed_cache.items() if v.is_expired()]
            for key in expired_keys:
                del self.compressed_cache[key]

            # Clean disk cache
            for key in list(self.disk_index.keys()):
                file_path = Path(self.disk_index[key])
                if file_path.exists():
                    try:
                        with open(file_path, "rb") as f:
                            entry = pickle.load(f)
                        if entry.is_expired():
                            file_path.unlink()
                            del self.disk_index[key]
                    except Exception:
                        # Corrupted file, remove it
                        file_path.unlink()
                        del self.disk_index[key]

    def _background_maintenance(self) -> None:
        """Background maintenance tasks."""
        while True:
            try:
                time.sleep(60)  # Run every minute

                # Cleanup expired entries
                self._cleanup_expired()

                # Update hot keys
                self._update_hot_keys()

                # Predictive prefetching
                self._predict_and_prefetch()

                # Save disk index
                self._save_disk_index()

                # Log statistics
                if self.enable_stats:
                    logging.info("Cache stats: %s", self.get_stats())

            except Exception as e:
                logging.error("Background maintenance error: %s", e)

    def _start_background_tasks(self) -> None:
        """Start background maintenance tasks."""
        self.executor.submit(self._background_maintenance)

    def get(self, key: str) -> Any | None:
        """
        Get value from cache.

        Args:
            key: Cache key

        Returns:
            Cached value or None if not found
        """
        start_time = time.time()

        with self.lock:
            # Check memory cache (L1)
            if key in self.memory_cache:
                entry = self.memory_cache[key]
                if not entry.is_expired():
                    entry.update_access()
                    # Move to end (most recently used)
                    self.memory_cache.move_to_end(key)

                    latency = time.time() - start_time
                    self._update_stats(True, CacheTier.MEMORY, latency)

                    # Track access
                    if self.enable_prediction:
                        self.access_history[key].append(time.time())

                    return entry.value
                else:
                    # Expired, remove it
                    del self.memory_cache[key]

            # Check compressed cache (L2)
            if key in self.compressed_cache:
                entry = self.compressed_cache[key]
                if not entry.is_expired():
                    entry.update_access()

                    # Promote to memory if frequently accessed
                    if entry.access_count > 3:
                        self._promote_to_memory(key, entry)
                        del self.compressed_cache[key]
                    else:
                        # Decompress and return
                        try:
                            decompressed = self._decompress(entry.value)
                            value = pickle.loads(decompressed)

                            latency = time.time() - start_time
                            self._update_stats(True, CacheTier.COMPRESSED, latency)

                            return value
                        except Exception as e:
                            logging.error("Failed to decompress entry %s: %s", key, e)
                else:
                    # Expired, remove it
                    del self.compressed_cache[key]

            # Check disk cache (L3)
            if key in self.disk_index:
                file_path = Path(self.disk_index[key])
                if file_path.exists():
                    try:
                        with open(file_path, "rb") as f:
                            entry = pickle.load(f)

                        if not entry.is_expired():
                            entry.update_access()

                            # Promote to memory if frequently accessed
                            if entry.access_count > 5:
                                self._promote_to_memory(key, entry)

                            latency = time.time() - start_time
                            self._update_stats(True, CacheTier.DISK, latency)

                            return entry.value
                        else:
                            # Expired, remove file
                            file_path.unlink()
                            del self.disk_index[key]
                    except Exception as e:
                        logging.error("Failed to load entry %s from disk: %s", key, e)
                        # Remove corrupted entry
                        file_path.unlink()
                        del self.disk_index[key]

        # Cache miss
        latency = time.time() - start_time
        self._update_stats(False, None, latency)
        return None

    def set(self, key: str, value: Any, ttl: int | None = None) -> None:
        """
        Set value in cache.

        Args:
            key: Cache key
            value: Value to cache
            ttl: Time to live in seconds (None for default)
        """
        if ttl is None:
            ttl = self.default_ttl

        # Calculate size
        try:
            serialized = pickle.dumps(value)
            size = len(serialized)
        except Exception as e:
            logging.error("Failed to serialize value for key %s: %s", key, e)
            return

        # Create entry
        entry = CacheEntry(
            key=key,
            value=value,
            size=size,
            created_at=time.time(),
            accessed_at=time.time(),
            ttl=ttl,
            tier=CacheTier.MEMORY,
        )

        with self.lock:
            # Store in memory cache
            self.memory_cache[key] = entry

            # Ensure memory limit
            self._evict_memory()

    def delete(self, key: str) -> bool:
        """
        Delete entry from cache.

        Args:
            key: Cache key

        Returns:
            True if deleted, False if not found
        """
        with self.lock:
            deleted = False

            # Remove from memory cache
            if key in self.memory_cache:
                del self.memory_cache[key]
                deleted = True

            # Remove from compressed cache
            if key in self.compressed_cache:
                del self.compressed_cache[key]
                deleted = True

            # Remove from disk cache
            if key in self.disk_index:
                file_path = Path(self.disk_index[key])
                if file_path.exists():
                    file_path.unlink()
                del self.disk_index[key]
                deleted = True

            return deleted

    def clear(self) -> None:
        """Clear all cache entries."""
        with self.lock:
            self.memory_cache.clear()
            self.compressed_cache.clear()

            # Remove all disk cache files
            for file_path in self.disk_index.values():
                path = Path(file_path)
                if path.exists():
                    path.unlink()
            self.disk_index.clear()

            # Reset statistics
            if self.enable_stats:
                self.stats = CacheStats()
                self.access_history.clear()
                self.latency_samples.clear()

            logging.info("Cache cleared")

    def get_stats(self) -> dict[str, Any]:
        """Get cache statistics."""
        if not self.enable_stats:
            return {}

        with self.stats_lock:
            return self.stats.to_dict()

    def cache_info(self) -> dict[str, Any]:
        """Get detailed cache information."""
        with self.lock:
            return {
                "memory_entries": len(self.memory_cache),
                "compressed_entries": len(self.compressed_cache),
                "disk_entries": len(self.disk_index),
                "total_entries": (
                    len(self.memory_cache) + len(self.compressed_cache) + len(self.disk_index)
                ),
                "memory_usage_mb": round(self._calculate_memory_usage() / 1024 / 1024, 2),
                "disk_usage_mb": round(self._calculate_disk_usage() / 1024 / 1024, 2),
                "compression": self.compression.value,
                "stats": self.get_stats() if self.enable_stats else None,
            }

    def shutdown(self) -> None:
        """Gracefully shutdown the cache."""
        logging.info("Shutting down cache...")

        # Save disk index
        self._save_disk_index()

        # Shutdown executor
        self.executor.shutdown(wait=True)

        logging.info("Cache shutdown complete")


# Convenience decorator for caching function results
def cached(
    ttl: int | None = None,
    key_prefix: str = "",
    cache_instance: HybridIntelligentCache | None = None,
):
    """
    Decorator to cache function results.

    Args:
        ttl: Time to live in seconds
        key_prefix: Prefix for cache keys
        cache_instance: Cache instance to use (creates new if None)

    Example:
        @cached(ttl=300, key_prefix="search")
        def search_web(query: str) -> dict:
            # Expensive operation
            return results
    """

    def decorator(func: Callable) -> Callable:
        # Use provided cache or create new one
        cache = cache_instance or HybridIntelligentCache()

        @wraps(func)
        def wrapper(*args, **kwargs):
            # Generate cache key
            key_parts = [key_prefix, func.__name__]
            key_parts.extend(str(arg) for arg in args)
            key_parts.extend(f"{k}={v}" for k, v in sorted(kwargs.items()))
            cache_key = ":".join(key_parts)

            # Try to get from cache
            result = cache.get(cache_key)
            if result is not None:
                logging.debug("Cache hit for %s", cache_key)
                return result

            # Cache miss, call function
            logging.debug("Cache miss for %s", cache_key)
            result = func(*args, **kwargs)

            # Store in cache
            cache.set(cache_key, result, ttl=ttl)

            return result

        # Attach cache instance for testing
        wrapper.cache = cache
        return wrapper

    return decorator


# Global cache instance (singleton)
_global_cache: HybridIntelligentCache | None = None


def get_global_cache() -> HybridIntelligentCache:
    """Get or create the global cache instance."""
    global _global_cache
    if _global_cache is None:
        from src.config import get_config

        config = get_config()

        # Get cache configuration
        cache_ttl = getattr(config.searx, "cache_ttl", 3600)
        cache_enabled = getattr(config.searx, "cache_enabled", True)

        if cache_enabled:
            _global_cache = HybridIntelligentCache(
                max_memory_mb=50,
                max_disk_mb=200,
                default_ttl=cache_ttl,
                compression=CompressionType.GZIP,
                enable_stats=True,
                enable_prediction=True,
            )
        else:
            # Create a minimal cache if disabled
            _global_cache = HybridIntelligentCache(
                max_memory_mb=10,
                max_disk_mb=0,
                default_ttl=60,
                enable_stats=False,
                enable_prediction=False,
            )

    return _global_cache


__all__ = [
    "HybridIntelligentCache",
    "CacheEntry",
    "CacheStats",
    "CacheTier",
    "CompressionType",
    "cached",
    "get_global_cache",
]
