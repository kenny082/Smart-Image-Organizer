"""Caching module for the API.

Implements metadata caching using LRU cache with file hash as key.
"""

import hashlib
import os
from datetime import datetime, timedelta
from functools import lru_cache
from pathlib import Path
from typing import Dict, Optional


class MetadataCache:
    """Metadata cache implementation using LRU cache."""

    def __init__(self, max_size: int = int(os.getenv("CACHE_SIZE", "1000"))):
        """
        Initialize the cache.

        Args:
            max_size: Maximum number of items to keep in cache
        """
        self.cache = lru_cache(maxsize=max_size)(self._get_metadata)
        self._storage: Dict[str, Dict] = {}
        self._timestamps: Dict[str, datetime] = {}
        self.ttl = timedelta(hours=1)  # Cache entries expire after 1 hour

    def _calculate_hash(self, file_path: Path) -> str:
        """
        Calculate file hash for cache key.

        Args:
            file_path: Path to the file

        Returns:
            str: MD5 hash of the file
        """
        hash_md5 = hashlib.md5()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_md5.update(chunk)
        return hash_md5.hexdigest()

    def _get_metadata(self, file_hash: str) -> Dict:
        """
        Get metadata from cache storage.

        Args:
            file_hash: Hash of the file

        Returns:
            Dict: Cached metadata or empty dict if not found
        """
        now = datetime.now()
        if (
            file_hash in self._timestamps
            and now - self._timestamps[file_hash] > self.ttl
        ):
            # Remove expired entries
            self._storage.pop(file_hash, None)
            self._timestamps.pop(file_hash, None)
            return {}

        return self._storage.get(file_hash, {})

    def get(self, file_path: Path) -> Optional[Dict]:
        """
        Get metadata from cache.

        Args:
            file_path: Path to the file

        Returns:
            Optional[Dict]: Cached metadata if found
        """
        file_hash = self._calculate_hash(file_path)
        return self.cache(file_hash)

    def set(self, file_path: Path, metadata: Dict) -> None:
        """
        Store metadata in cache.

        Args:
            file_path: Path to the file
            metadata: Metadata to cache
        """
        file_hash = self._calculate_hash(file_path)
        self._storage[file_hash] = metadata
        self._timestamps[file_hash] = datetime.now()
        # Clear the LRU cache to force recomputation
        self.cache.cache_clear()

    def clear(self) -> None:
        """Clear the cache."""
        self._storage.clear()
        self._timestamps.clear()
        self.cache.cache_clear()

    def get_stats(self) -> Dict:
        """
        Get cache statistics.

        Returns:
            Dict: Cache statistics
        """
        return {
            "size": len(self._storage),
            "hits": self.cache.cache_info().hits,
            "misses": self.cache.cache_info().misses,
        }


# Global cache instance
metadata_cache = MetadataCache()
