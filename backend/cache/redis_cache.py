"""
Caching layer with Redis support and in-memory fallback
"""
import json
import logging
from typing import Optional, Dict, Any
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

# Try to import Redis, but allow fallback to in-memory cache
try:
    import redis.asyncio as redis
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False
    logger.warning("Redis not available, using in-memory cache")


class CacheManager:
    """
    Cache manager with Redis support and in-memory fallback.
    Automatically falls back to in-memory if Redis is not configured or unavailable.
    """

    def __init__(
        self,
        redis_host: str = "localhost",
        redis_port: int = 6379,
        redis_password: Optional[str] = None,
        redis_enabled: bool = False
    ):
        """
        Initialize cache manager

        Args:
            redis_host: Redis server host
            redis_port: Redis server port
            redis_password: Redis password (optional)
            redis_enabled: Whether to use Redis (if False, uses in-memory cache)
        """
        self.redis_client: Optional[redis.Redis] = None
        self.use_redis = redis_enabled and REDIS_AVAILABLE
        self.in_memory_cache: Dict[str, tuple[Any, datetime]] = {}

        if self.use_redis:
            try:
                self.redis_client = redis.Redis(
                    host=redis_host,
                    port=redis_port,
                    password=redis_password,
                    decode_responses=True
                )
                logger.info(f"Redis cache initialized: {redis_host}:{redis_port}")
            except Exception as e:
                logger.warning(f"Failed to connect to Redis: {e}. Using in-memory cache.")
                self.use_redis = False
        else:
            logger.info("Using in-memory cache (Redis disabled or unavailable)")

    async def get(self, key: str) -> Optional[Dict]:
        """
        Retrieve value from cache

        Args:
            key: Cache key

        Returns:
            Cached value or None if not found
        """
        if self.use_redis and self.redis_client:
            try:
                value = await self.redis_client.get(key)
                if value:
                    logger.debug(f"Cache hit (Redis): {key}")
                    return json.loads(value)
            except Exception as e:
                logger.error(f"Redis get error: {e}")
                return None
        else:
            # In-memory cache
            if key in self.in_memory_cache:
                value, expiry = self.in_memory_cache[key]
                if datetime.now() < expiry:
                    logger.debug(f"Cache hit (in-memory): {key}")
                    return value
                else:
                    # Expired, remove it
                    del self.in_memory_cache[key]

        logger.debug(f"Cache miss: {key}")
        return None

    async def set(self, key: str, value: Dict, ttl: int = 86400) -> bool:
        """
        Store value in cache

        Args:
            key: Cache key
            value: Value to cache (must be JSON serializable)
            ttl: Time to live in seconds (default: 24 hours)

        Returns:
            True if successful
        """
        if self.use_redis and self.redis_client:
            try:
                await self.redis_client.setex(
                    key,
                    ttl,
                    json.dumps(value)
                )
                logger.debug(f"Cached (Redis): {key} (TTL: {ttl}s)")
                return True
            except Exception as e:
                logger.error(f"Redis set error: {e}")
                return False
        else:
            # In-memory cache
            expiry = datetime.now() + timedelta(seconds=ttl)
            self.in_memory_cache[key] = (value, expiry)
            logger.debug(f"Cached (in-memory): {key} (TTL: {ttl}s)")
            return True

    async def delete(self, key: str) -> bool:
        """
        Delete value from cache

        Args:
            key: Cache key

        Returns:
            True if successful
        """
        if self.use_redis and self.redis_client:
            try:
                await self.redis_client.delete(key)
                return True
            except Exception as e:
                logger.error(f"Redis delete error: {e}")
                return False
        else:
            # In-memory cache
            if key in self.in_memory_cache:
                del self.in_memory_cache[key]
            return True

    async def clear_all(self) -> bool:
        """
        Clear all cached values

        Returns:
            True if successful
        """
        if self.use_redis and self.redis_client:
            try:
                await self.redis_client.flushdb()
                logger.info("Redis cache cleared")
                return True
            except Exception as e:
                logger.error(f"Redis clear error: {e}")
                return False
        else:
            # In-memory cache
            self.in_memory_cache.clear()
            logger.info("In-memory cache cleared")
            return True

    async def is_connected(self) -> bool:
        """
        Check if Redis is connected (always True for in-memory)

        Returns:
            True if connected or using in-memory cache
        """
        if self.use_redis and self.redis_client:
            try:
                await self.redis_client.ping()
                return True
            except Exception:
                return False
        else:
            # In-memory cache is always "connected"
            return True

    def get_stats(self) -> Dict[str, Any]:
        """
        Get cache statistics

        Returns:
            Dictionary with cache statistics
        """
        if self.use_redis:
            return {
                "type": "redis",
                "enabled": True,
                "connected": self.redis_client is not None
            }
        else:
            return {
                "type": "in-memory",
                "enabled": True,
                "items": len(self.in_memory_cache)
            }
