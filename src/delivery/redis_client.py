from typing import Optional

import redis.asyncio as redis

from delivery.logger import logger

redis_client: redis.Redis | None = None


async def init_redis() -> redis.Redis:
    global redis_client
    redis_client = redis.Redis(host="localhost", port=6379, encoding="utf-8", decode_responses=True)
    await redis_client.ping()
    logger.info("Redis connected")
    return redis_client


async def close_redis():
    global redis_client
    if redis_client:
        await redis_client.close()
        logger.info("Redis connection closed")
        redis_client = None
