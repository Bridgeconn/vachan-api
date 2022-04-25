from datetime import timedelta
import json
import redis
from dependencies import log
from custom_exceptions import UnAuthorizedException

# redis connection
def redis_connect() -> redis.client.Redis:
    try:
        client = redis.Redis(
            host="redis",
            # host="localhost",
            port=6379,
            db=0,
            socket_timeout=5,
        )
        ping = client.ping()
        if ping is True:
            log.warning("redis ping successfull ------------------")
            return client
    except redis.AuthenticationError:
        log.error("AuthenticationError xxxxxxxxxxxxxxx")
        raise UnAuthorizedException("Redis Connection Failed")

def get_routes_from_cache(key: str):
    """Data from redis."""
    redis_client = redis_connect()
    val = redis_client.get(key)
    return val

def set_routes_to_cache(key: str, value: str):
    """Data to redis."""
    redis_client = redis_connect()
    state = redis_client.setex(key, timedelta(seconds=180), value=value)
    return state

async def validate_cache(route_url: str, source_func, *args):
    """check cache present or not"""
    data = get_routes_from_cache(key= route_url)
    
    if data is None:
        data = source_func(*args)
        state = set_routes_to_cache(key=route_url, value=data)
        if state is True:
            return data
        else:
            print("Data not stored in cache")
    else:
        data = json.loads(data)
        return data

