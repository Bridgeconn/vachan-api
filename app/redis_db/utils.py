''' Redis Db Connection and util functions'''
from datetime import timedelta
import redis
from dependencies import log
from custom_exceptions import UnAuthorizedException

# redis connection
def redis_connect() -> redis.client.Redis:
    """Connect Reddis"""
    try:
        log.info('In redis connection util')
        client = redis.Redis(
            host="redis",
            # host="localhost",
            port=6379,
            db=0,
            socket_timeout=5,
        )
        ping = client.ping()
        if ping is True:
            log.info("redis ping successfull ------------------")
            return client
        raise Exception(redis.RedisError)
    except redis.AuthenticationError as redis_auth_error:
        log.error("AuthenticationError xxxxxxxxxxxxxxx")
        raise UnAuthorizedException("Redis Connection Failed") from redis_auth_error

def get_routes_from_cache(key: str):
    """Data from redis."""
    log.info('In redis get data')
    redis_client = redis_connect()
    val = redis_client.get(key)
    return val

def set_routes_to_cache(key: str, value: str):
    """Data to redis."""
    log.info('In redis set data')
    redis_client = redis_connect()
    state = redis_client.setex(key, timedelta(seconds=180), value=value)
    return state

def del_cache(key: str):
    """del cache data"""
    log.info('In redis delete data')
    redis_client = redis_connect()
    val = redis_client.delete(key)
    return val
