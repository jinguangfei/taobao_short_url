from pydantic_core import MultiHostUrl
from pydantic import (
    PostgresDsn,
    computed_field,
)

class DBInfo(object):
    class MySQLDB(object):
        HOST = "127.0.0.1"
        PORT = 3306
        USERNAME = "root"
        PASSWD = "zhihai"
        DBNAME = "source"

        URL =  f"mysql+pymysql://{USERNAME}:{PASSWD}@{HOST}:{PORT}/{DBNAME}"

    class RedisDB(object):
        HOST = "127.0.0.1"
        PORT = 6379
        DB = 6
        PASSWORD = ""

        MAX_CONNECTIONS = 25
        # 有限轮询
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