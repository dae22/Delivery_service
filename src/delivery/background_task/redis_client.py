import redis

from delivery.settings import REDIS_URL

redis_client = redis.from_url(REDIS_URL)
