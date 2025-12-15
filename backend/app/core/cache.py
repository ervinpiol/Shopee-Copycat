from redis.asyncio import Redis
from typing import Optional

CACHE_TTL = 300  # default TTL for all caches

class CacheManager:
    def __init__(self, redis: Redis):
        self.redis = redis

    async def invalidate(self, key: str) -> None:
        """Invalidate a cache by key"""
        await self.redis.delete(key)

    async def set(self, key: str, value: str, ttl: Optional[int] = None) -> None:
        """Set a cache value with optional TTL"""
        await self.redis.set(key, value, ex=ttl or CACHE_TTL)

    async def get(self, key: str) -> Optional[str]:
        """Get a cached value"""
        return await self.redis.get(key)
