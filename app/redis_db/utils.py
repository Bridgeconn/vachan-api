''' Redis Db Connection and util functions'''
import os
from datetime import timedelta
import redis
from dependencies import log
from custom_exceptions import UnAuthorizedException

# redis connection
def redis_connect() -> redis.client.Redis:
    """Connect Reddis"""
    redis_host = os.environ.get("VACHAN_REDIS_HOST", "redis")
    redis_port = os.environ.get("VACHAN_REDIS_PORT", 6379)
    redis_pass = os.environ.get("VACHAN_REDIS_PASS", "XXX")

    try:
        log.info('In redis connection util')
        client = redis.Redis(
            host=redis_host,
            password=redis_pass,
            port=redis_port,
            db=0,
            socket_timeout=5,
        )
        ping = client.ping()
        if ping is True:
            log.info("redis ping successfull ------------------")
            return client
        raise Exception(redis.RedisError)
    except redis.AuthenticationError as redis_auth_error:
        log.error("Auth error from Redis!!!")
        raise UnAuthorizedException("Redis Connection Failed") from redis_auth_error
    except Exception as any_error: #pylint: disable=W0703
        log.error("Redis connection failed. May be Redis container is not running at %s:%s.",
            redis_host, redis_port)
        log.error(any_error)
        # not raisig error to be able to function even without redis, eg. local dev
        return None

def get_routes_from_cache(key: str):
    """Data from redis."""
    log.info('In redis get data')
    redis_client = redis_connect()
    val = None
    if redis_client is not None:
        val = redis_client.get(key)
    if val is not None:
        log.info("Redis: cache hit!!!!!!!!")
    else:
        log.info("Redis: cache miss~~~~~~~~~~~")
    return val

def set_routes_to_cache(key: str, value: str):
    """Data to redis."""
    log.info('In redis set data')
    redis_client = redis_connect()
    state = None
    if redis_client is not None:
        state = redis_client.setex(key, timedelta(days=100), value=value)
        log.info("Redis: cache update $$$$$$$$$$$$$")
    return state

def del_cache(key: str):
    """del cache data"""
    log.info('In redis delete data')
    redis_client = redis_connect()
    val = None
    if redis_client is not None:
        val = redis_client.delete(key)
    return val
