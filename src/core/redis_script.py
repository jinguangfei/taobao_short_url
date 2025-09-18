from redis import StrictRedis, ConnectionPool
from typing import Callable, Tuple, Optional
import time

class RedisSettings(object):
    REDIS_HOST: str = "127.0.0.1"
    REDIS_HOST: str = "39.106.91.99"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 12
    REDIS_PASSWORD: str = "zhihai_niersen_cookie_use_456789047"
    REDIS_MAX_CONNECTIONS: int = 100
    REDIS_SECRET_KEY : str = "dcx"

def get_redis_pool(settings : RedisSettings) -> StrictRedis:
    return StrictRedis(connection_pool=ConnectionPool(
        host=settings.REDIS_HOST, 
        port=settings.REDIS_PORT, 
        db=settings.REDIS_DB,
        password=settings.REDIS_PASSWORD,
        max_connections=settings.REDIS_MAX_CONNECTIONS))    
zadd_with_scores = """
    local handle_key = KEYS[1]
    local add_t = tonumber(ARGV[1])
    local start_t = tonumber(ARGV[2])
    local end_t = tonumber(ARGV[3])
    local level = tonumber(ARGV[4])
    local loop_type = tonumber(ARGV[5])
    local key_list_info = {}
    if loop_type == 1 then
        key_list_info = redis.call('ZREVRANGEBYSCORE',handle_key,start_t,end_t,'WITHSCORES')
    elseif loop_type == 2 then
        key_list_info = redis.call('ZRANGE',handle_key,0,1,'WITHSCORES')
    end
    if #key_list_info >= 2 then
        local one_key = key_list_info[1]
        local one_key_t = tonumber(key_list_info[2])
        if (start_t + level >= one_key_t) then
            local next_t = start_t + add_t
            redis.call('zadd',handle_key,next_t,one_key)
            return {one_key,one_key_t,next_t}
        else
            return {"",0,0}
        end
    else
        return {"",0,0}
    end
"""

zadd_with_id = """
local handle_key = KEYS[1]
local add_t = tonumber(ARGV[1])
local cur_t = tonumber(ARGV[2])
local one_key = ARGV[3]
local one_key_t = tonumber(redis.call('ZSCORE',handle_key,one_key) or 0)
if (cur_t >= one_key_t) then
    local next_t = cur_t + add_t
    redis.call('zadd',handle_key,next_t,one_key)
    return {one_key,one_key_t,next_t}
else
    return {"",0,0}
end
"""
choke_script = """
local handle_key = KEYS[1]
local handler_key_lasttime = handle_key .. "_lasttime"
local token_key = ARGV[1]
local cur_time = tonumber(ARGV[2])
local capacity = tonumber(ARGV[3])
local rate = tonumber(ARGV[4])

local last_time = tonumber(redis.call('HGET', handler_key_lasttime, token_key) or 0)
local token_value = tonumber(redis.call('HGET', handle_key, token_key) or 0)

local add_value = math.max((cur_time-last_time),0) / rate
local token_value_max = math.min(capacity, token_value + add_value)
redis.call('HSET', handler_key_lasttime, token_key, cur_time)
if (token_value_max >= 1) then
    redis.call('HSET', handle_key, token_key, token_value_max - 1)
    return 1
else
    redis.call('HSET', handle_key, token_key, token_value_max)
    return 0
end
"""
zpop_min = """
local handle_key = KEYS[1]
local one_key = redis.call('ZRANGE', handle_key, 0, 0, 'WITHSCORES')
if #one_key >= 2 then
    redis.call('ZREM', handle_key, one_key[1])
end
return one_key
"""

redis_pool = get_redis_pool(RedisSettings())

zadd_with_scores = redis_pool.register_script(zadd_with_scores)
zadd_with_id = redis_pool.register_script(zadd_with_id)
h_choke_func = redis_pool.register_script(choke_script)
zpop_min = redis_pool.register_script(zpop_min)

def loop_r(view_redis_key : str, add_t : int = 20, start_t : int = 0, end_t : int = 0, level : int = 0, loop_type : int = 1) -> Tuple[str,int,int]:
    """
    获取队列中的一个元素
    add_t: 元素的过期时间
    start_t: 元素的开始时间
    end_t: 元素的结束时间
    level: 元素的级别
    loop_type: 元素的循环类型(1: 从大到小, 2: 从小到大)
    :return: 元素的key, 元素的过期时间, 元素的下一个过期时间
    """
    one_key_t,next_t = 0,0
    try:
        start_t = start_t if start_t else int(time.time())
        end_t = end_t if end_t else 0
        one_key, one_key_t, next_t = zadd_with_scores(keys=[view_redis_key],args=[add_t,start_t,end_t,level,loop_type])
        one_key : bytes
        one_key = one_key.decode("utf-8")
    except Exception as e:
        pass
    return one_key, one_key_t, next_t 

def choke_func(handler_key : str, token: str, capacity : int = 5, rate : float = 0.5) -> bool:
    """
    限制令牌
    """
    cur_time = int(time.time())
    flag = h_choke_func(keys=[handler_key],args=[token,cur_time,capacity,rate])
    return bool(int(flag))