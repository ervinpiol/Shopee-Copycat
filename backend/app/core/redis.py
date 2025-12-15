import redis.asyncio as redis
from typing import Optional
from app.core.config import settings

class RedisClient:
    _client: Optional[redis.Redis] = None

    @classmethod
    async def init(cls) -> None:
        if cls._client is None:
            cls._client = redis.from_url(
                settings.redis_url,
                encoding="utf-8",
                decode_responses=True,
                max_connections=20,
                socket_connect_timeout=5,
                socket_timeout=5,
                health_check_interval=30,
            )
            await cls._client.ping()

    @classmethod
    def get(cls) -> redis.Redis:
        if cls._client is None:
            raise RuntimeError("Redis client not initialized")
        return cls._client

    @classmethod
    async def close(cls) -> None:
        if cls._client:
            await cls._client.aclose()
            cls._client = None


def get_redis() -> redis.Redis:
    """FastAPI dependency"""
    return RedisClient.get()
