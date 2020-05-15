import os
from .cache import Cache
from .redis_cache import RedisCache


def create_cache():
    redis_server = os.getenv("DC_REDIS_HOST")
    if redis_server is None:
        return Cache()

    return RedisCache(
        **{
            "host": redis_server,
            "db": int(os.getenv("DC_REDIS_DB", "0")),
            "password": os.getenv("DC_REDIS_PASSWORD"),
            "port": int(os.getenv("DC_REDIS_PORT", "6379")),
            "max_age": int(os.getenv("DC_REDIS_MAX_AGE", "1800")),
        }
    )
