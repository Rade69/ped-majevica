"""
Redis Caching utilities for Flask API responses
"""

from flask import request, jsonify
from functools import wraps
import redis
import json
import logging
import hashlib
from typing import Any, Optional, Callable

logger = logging.getLogger(__name__)

# Global Redis client
redis_client = None


def init_redis(app):
    """
    Initialize Redis connection
    Call this in your application factory
    """
    global redis_client

    redis_url = app.config.get("REDIS_URL", "redis://localhost:6379/0")

    try:
        redis_client = redis.from_url(redis_url, decode_responses=True)
        # Test connection
        redis_client.ping()
        logger.info(f"✅ Redis connected: {redis_url}")
    except Exception as e:
        logger.warning(f"⚠️ Redis connection failed: {e}. Caching disabled.")
        redis_client = None

    return redis_client


def get_redis():
    """Get Redis client"""
    return redis_client


def generate_cache_key(prefix: str, **kwargs) -> str:
    """
    Generate a unique cache key based on endpoint and parameters

    Args:
        prefix: Key prefix (e.g., 'api_posts')
        **kwargs: Parameters to include in key

    Returns:
        Cache key string
    """
    # Sort keys for consistent hashing
    params = sorted(kwargs.items())
    params_str = json.dumps(params, sort_keys=True)

    # Create hash of params
    params_hash = hashlib.md5(params_str.encode()).hexdigest()[:8]

    return f"{prefix}:{params_hash}"


def get_cached(key: str) -> Optional[Any]:
    """Get value from cache"""
    if not redis_client:
        return None

    try:
        value = redis_client.get(key)
        if value:
            return json.loads(value)
    except Exception as e:
        logger.warning(f"Cache get error: {e}")

    return None


def set_cached(key: str, value: Any, ttl: int = 300) -> bool:
    """Set value in cache with TTL"""
    if not redis_client:
        return False

    try:
        redis_client.setex(key, ttl, json.dumps(value))
        return True
    except Exception as e:
        logger.warning(f"Cache set error: {e}")
        return False


def delete_cached(key: str) -> bool:
    """Delete value from cache"""
    if not redis_client:
        return False

    try:
        redis_client.delete(key)
        return True
    except Exception as e:
        logger.warning(f"Cache delete error: {e}")
        return False


def invalidate_prefix(prefix: str) -> bool:
    """Invalidate all keys with given prefix"""
    if not redis_client:
        return False

    try:
        # Find all keys with prefix
        keys = redis_client.keys(f"{prefix}:*")
        if keys:
            redis_client.delete(*keys)
            logger.info(f"Invalidated {len(keys)} cache keys for prefix: {prefix}")
        return True
    except Exception as e:
        logger.warning(f"Cache invalidate error: {e}")
        return False


def cache_response(ttl: int = 300, prefix: Optional[str] = None):
    """
    Decorator to cache API responses

    Args:
        ttl: Time to live in seconds (default: 5 minutes)
        prefix: Custom cache key prefix (default: endpoint path)

    Usage:
        @cache_response(ttl=60, prefix='api_posts')
        def get_posts():
            ...
    """

    def decorator(f: Callable) -> Callable:
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not redis_client:
                return f(*args, **kwargs)

            # Generate cache key from request
            cache_prefix = prefix or request.path.replace("/", "_").strip("_")

            # Include query params in key
            cache_params = dict(request.args)

            # Add user-specific params if needed
            from flask_login import current_user

            if current_user.is_authenticated:
                cache_params["user_id"] = current_user.id

            cache_key = generate_cache_key(cache_prefix, **cache_params)

            # Try to get from cache
            cached_data = get_cached(cache_key)
            if cached_data is not None:
                logger.debug(f"Cache HIT: {cache_key}")
                return jsonify(cached_data)

            # Execute function
            logger.debug(f"Cache MISS: {cache_key}")
            response = f(*args, **kwargs)

            # Cache successful responses
            if hasattr(response, "get_json"):
                try:
                    data = response.get_json()
                    if data and response.status_code == 200:
                        set_cached(cache_key, data, ttl)
                except Exception:
                    pass

            return response

        return decorated_function

    return decorator


def cache_invalidate_on_change(*prefixes: str):
    """
    Decorator to invalidate cache after data modification

    Usage:
        @cache_invalidate_on_change('api_posts', 'api_events')
        def create_post():
            ...
    """

    def decorator(f: Callable) -> Callable:
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Execute function
            response = f(*args, **kwargs)

            # Invalidate cache on success
            if hasattr(response, "status_code") and response.status_code in (200, 201):
                for prefix in prefixes:
                    invalidate_prefix(prefix)

            return response

        return decorated_function

    return decorator


# Convenience functions for manual caching
class Cache:
    """Cache manager class"""

    @staticmethod
    def get(key: str) -> Optional[Any]:
        return get_cached(key)

    @staticmethod
    def set(key: str, value: Any, ttl: int = 300) -> bool:
        return set_cached(key, value, ttl)

    @staticmethod
    def delete(key: str) -> bool:
        return delete_cached(key)

    @staticmethod
    def invalidate(prefix: str) -> bool:
        return invalidate_prefix(prefix)

    @staticmethod
    def clear() -> bool:
        """Clear all cache"""
        if not redis_client:
            return False
        try:
            redis_client.flushdb()
            logger.info("✅ Cache cleared")
            return True
        except Exception as e:
            logger.warning(f"Cache clear error: {e}")
            return False
