import time
import threading
from functools import wraps
from flask import request, current_app, jsonify

class MemoryCache:
    """
    Thread-safe, high-performance in-memory cache with TTL and prefix-based invalidation.
    Designed with graceful degradation: if any cache failure occurs, it transparently
    falls back to live computation without interrupting application execution.
    """
    def __init__(self):
        self._cache = {}
        self._lock = threading.Lock()
        self.hits = 0
        self.misses = 0

    def get(self, key):
        """Retrieve an unexpired value from the cache."""
        try:
            with self._lock:
                item = self._cache.get(key)
                if item is None:
                    self.misses += 1
                    return None
                val, expires_at = item
                if expires_at is not None and time.time() > expires_at:
                    del self._cache[key]
                    self.misses += 1
                    return None
                self.hits += 1
                return val
        except Exception:
            return None

    def set(self, key, value, ttl=60):
        """Store a value with an expiration TTL (in seconds)."""
        try:
            expires_at = time.time() + ttl if ttl and ttl > 0 else None
            with self._lock:
                self._cache[key] = (value, expires_at)
        except Exception:
            pass

    def delete(self, key):
        """Delete a single key from cache."""
        try:
            with self._lock:
                self._cache.pop(key, None)
        except Exception:
            pass

    def invalidate_prefix(self, prefix):
        """
        Invalidate all cached entries matching a key prefix/tag.
        Example: invalidate_prefix('departments') purges all departmental cache entries.
        """
        try:
            with self._lock:
                keys_to_delete = [k for k in self._cache.keys() if k.startswith(prefix)]
                for k in keys_to_delete:
                    del self._cache[k]
        except Exception:
            pass

    def clear(self):
        """Purge all stored cache entries."""
        try:
            with self._lock:
                self._cache.clear()
        except Exception:
            pass

    def get_stats(self):
        """Return cache hit/miss statistics and entry count."""
        with self._lock:
            return {
                'total_keys': len(self._cache),
                'hits': self.hits,
                'misses': self.misses,
                'hit_ratio': round(self.hits / (self.hits + self.misses), 2) if (self.hits + self.misses) > 0 else 0.0
            }

# Global cache instance
cache_store = MemoryCache()

def is_cache_active():
    """Check if caching is enabled in app configuration."""
    try:
        return current_app.config.get('CACHE_ENABLED', True)
    except RuntimeError:
        return True

def cached(ttl=60, prefix=''):
    """
    Decorator for caching endpoint responses or helper functions.
    Constructs cache keys based on endpoint prefix and query parameters.
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not is_cache_active():
                return f(*args, **kwargs)

            try:
                # Build unique cache key including request query parameters
                query_items = tuple(sorted(request.args.items())) if request else ()
                key_prefix = prefix or f.__name__
                cache_key = f"{key_prefix}:{hash(query_items)}:{hash(args)}:{hash(frozenset(kwargs.items()))}"

                cached_val = cache_store.get(cache_key)
                if cached_val is not None:
                    # If cached value is JSON response data dict, return JSON response
                    if isinstance(cached_val, dict):
                        return jsonify(cached_val)
                    return cached_val

                # Execute original function
                result = f(*args, **kwargs)

                # Store response in cache (handling Flask Response or dict)
                if hasattr(result, 'get_json') and result.is_json:
                    cache_store.set(cache_key, result.get_json(), ttl=ttl)
                elif isinstance(result, (dict, list, str)):
                    cache_store.set(cache_key, result, ttl=ttl)

                return result
            except Exception:
                # Fail gracefully by executing function normally
                return f(*args, **kwargs)
        return decorated_function
    return decorator

def invalidate_cache(prefix):
    """Public helper to invalidate cache by tag/prefix."""
    cache_store.invalidate_prefix(prefix)

def clear_all_cache():
    """Public helper to flush all cache entries."""
    cache_store.clear()
