"""
Simple cache system for API calls to improve efficiency.
"""

import hashlib
import json
import time
from typing import Any, Dict, Optional


class SimpleCache:
    """
    Simple in-memory cache with TTL (time-to-live).
    Follows Anthropic's "start simple" principle.
    """
    
    def __init__(self, default_ttl_seconds: int = 3600):  # 1 hour default
        self.cache: Dict[str, Dict[str, Any]] = {}
        self.default_ttl = default_ttl_seconds
    
    def _make_key(self, function_name: str, *args, **kwargs) -> str:
        """Create a cache key from function name and arguments."""
        # Create a stable hash from function name and arguments
        key_data = {
            'function': function_name,
            'args': args,
            'kwargs': kwargs
        }
        key_string = json.dumps(key_data, sort_keys=True, default=str)
        return hashlib.md5(key_string.encode()).hexdigest()
    
    def get(self, function_name: str, *args, **kwargs) -> Optional[Any]:
        """Get cached result if available and not expired."""
        cache_key = self._make_key(function_name, *args, **kwargs)
        
        if cache_key not in self.cache:
            return None
        
        cached_data = self.cache[cache_key]
        
        # Check if expired
        if time.time() > cached_data['expires_at']:
            del self.cache[cache_key]
            return None
        
        print(f"🔄 Cache hit for {function_name}")
        return cached_data['result']
    
    def set(self, function_name: str, result: Any, ttl_seconds: Optional[int] = None, *args, **kwargs):
        """Store result in cache with TTL."""
        cache_key = self._make_key(function_name, *args, **kwargs)
        ttl = ttl_seconds or self.default_ttl
        
        self.cache[cache_key] = {
            'result': result,
            'expires_at': time.time() + ttl,
            'created_at': time.time()
        }
        
        import logging
        logger = logging.getLogger(__name__)
        logger.info(f"Cached result for {function_name} (TTL: {ttl}s)")
    
    def clear(self):
        """Clear all cached data."""
        self.cache.clear()
        print("🧹 Cache cleared")
    
    def cleanup_expired(self):
        """Remove expired entries."""
        current_time = time.time()
        expired_keys = [
            key for key, data in self.cache.items()
            if current_time > data['expires_at']
        ]
        
        for key in expired_keys:
            del self.cache[key]
        
        if expired_keys:
            print(f"🧹 Cleaned up {len(expired_keys)} expired cache entries")
    
    def stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        self.cleanup_expired()
        return {
            'total_entries': len(self.cache),
            'cache_size_mb': len(str(self.cache)) / (1024 * 1024)
        }


# Global cache instance
cache = SimpleCache()


def cached(ttl_seconds: int = 3600):
    """
    Simple decorator to cache function results.
    
    Usage:
    @cached(ttl_seconds=1800)  # 30 minutes
    async def expensive_api_call(param):
        return await some_api_call(param)
    """
    def decorator(func):
        async def wrapper(*args, **kwargs):
            # Check cache first
            cached_result = cache.get(func.__name__, *args, **kwargs)
            if cached_result is not None:
                return cached_result
            
            # Execute function and cache result
            result = await func(*args, **kwargs)
            cache.set(func.__name__, result, ttl_seconds, *args, **kwargs)
            
            return result
        
        return wrapper
    return decorator