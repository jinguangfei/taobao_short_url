from __future__ import annotations
import time
import traceback
from typing import Optional, List, Dict, Tuple, Type, Union, ClassVar, TypeVar, NewType
from redis import StrictRedis

from .redis_script import (
    zadd_with_scores,
    zadd_with_id,
    get_redis_pool,
    RedisSettings,
)

Count = NewType("Count", int)
OneKey = NewType("OneKey", str)
Prev_t= NewType("Prev_t", int)
Next_t = NewType("Next_t", int)

TableName = NewType("TableName", str)
ViewName = NewType("ViewName", str)
ViewInfo = Tuple[TableName,ViewName]

class RedisView(object):
    VIEW_DICT : Dict[ViewInfo,RedisView] = dict()
    
    def __new__(cls, table_name: str = "", view_name: str = "", **kwargs):
        key = (table_name, view_name)

        if key in cls.VIEW_DICT:
            return cls.VIEW_DICT[key]
        instance = super().__new__(cls)
        cls.VIEW_DICT[key] = instance
        return instance

    def __init__(self, table_name : str = "", view_name : str = "", redis : Optional[StrictRedis] = None, **kwargs):
        # 防止重复初始化
        if hasattr(self, 'table_name'):
            return
        self.redis = redis
        self.zadd_with_scores = self.redis.register_script(zadd_with_scores)
        self.zadd_with_id = self.redis.register_script(zadd_with_id)

        self.table_name = table_name
        self.view_name = view_name

        self.view_key_prev = f"view:{RedisSettings.REDIS_SECRET_KEY}"
        self.view_redis_key = f"{self.view_key_prev}:{table_name}:{view_name}"

    def get_r(self, one_key : OneKey = "", add_t : int = 20, **kwargs) -> Tuple[OneKey,Prev_t,Next_t]:
        """
        获取队列中的一个元素
        add_t: 元素的过期时间
        :return: 元素的key, 元素的过期时间, 元素的下一个过期时间
        """
        one_key_t, next_t = 0, 0
        try:
            cur_t = int(time.time())
            one_key, one_key_t, next_t = self.zadd_with_id(keys=[self.view_redis_key],args=[add_t,cur_t,one_key])
            one_key : bytes
            one_key = one_key.decode("utf-8")
        except Exception as e:
            pass
        return one_key, one_key_t, next_t 

    def loop_r(self, add_t : int = 20, start_t : Optional[int] = None, end_t : Optional[int] = None, level : int = 0, loop_type : int = 1, **kwargs) -> Tuple[OneKey,Prev_t,Next_t]:
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
            start_t = start_t if start_t is not None else 0
            end_t = end_t if end_t is not None else 0
            one_key, one_key_t, next_t = self.zadd_with_scores(keys=[self.view_redis_key],args=[add_t,start_t,end_t,level,loop_type])
            one_key : bytes
            one_key = one_key.decode("utf-8")
        except Exception as e:
            pass
        return one_key, one_key_t, next_t 

    def range_r(self, start_t : int = 0, end_t : int = 0) -> List[Tuple[OneKey,Prev_t]]:
        all_key_list : List[Tuple[bytes,float]] = self.redis.zrangebyscore(self.view_redis_key, start_t, end_t, withscores=True)
        all_key_list = [(one_key.decode("utf-8"),t) for one_key,t in all_key_list]
        return all_key_list

    def count_r(self) -> Count:
        return self.redis.zcard(self.view_redis_key)

    def all_view_count_r(self) -> Dict[ViewInfo,Count]:
        result = dict()
        for view_info, view in self.VIEW_DICT.items():
            result[view_info] = view.count_r()
        return result

    def add_r(self, one_key : OneKey, t : int = 0) -> None:
        self.redis.zadd(self.view_redis_key, {one_key: t})

    def wait_r(self, one_key : OneKey, add_t : int =60*60*24) -> None:
        if not self.redis.zscore(self.view_redis_key, one_key) is None:
            t = int(time.time())
            next_t = t + add_t
            self.redis.zadd(self.view_redis_key, {one_key: next_t})

    def delete_r(self, one_key : OneKey) -> None:
        return self.redis.zrem(self.view_redis_key, one_key)

    def delete_all_r(self) -> None:
        return self.redis.delete(self.view_redis_key) 

    def trim_r(self, start_t : int = 0, end_t : int = 0) -> None:
        self.redis.zremrangebyscore(self.view_redis_key,start_t,end_t)

    def remove_view_r(self):
        self.VIEW_DICT.pop((self.table_name,self.view_name))
        self.redis.delete(self.view_redis_key)
    
    def __del__(self):
        print(f"del {self.table_name}:{self.view_name}")

if __name__ == '__main__':
    redis_pool = get_redis_pool(RedisSettings)

    view =  RedisView(table_name="test",view_name="test",redis=redis_pool)
    view.remove_view_r()
    view =  RedisView(table_name="test1",view_name="test",redis=redis_pool)
    view_info_dict = view.all_view_count_r()
    for view_info,count in view_info_dict.items():
        table_name = view_info[0]
        view_name = view_info[1]
        print(f"{table_name}:{view_name} 有 {count} 个元素")
