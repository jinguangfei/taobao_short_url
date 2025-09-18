import asyncio
from re import I
import time
from src.core.redis_script import redis_pool, zpop_min

class ConfigTask(object):
    def __init__(self):
        self.redis = redis_pool
        self.task_key = "config:task"
        self.result_key = "config:result"

    def add_task(self, url : str) -> None:
        self.redis.zadd(self.task_key, {url: int(time.time())})

    def get_task(self):
        # zpop
        self.redis.zremrangebyscore(self.task_key, 0, int(time.time()) - 10)
        url = zpop_min(keys=[self.task_key])
        if url:
            url = url[0].decode("utf-8")
            return url

    def over_task(self, url: str, result: str) -> None:
        self.redis.hset(self.result_key, url, result)

    # 等待timeout秒，获取结果
    async def get_result(self,  url: str, timeout : int = 10) -> str | None:
        result = None
        start_time = int(time.time())
        while int(time.time()) - start_time < timeout:
            result : bytes = self.redis.hget(self.result_key, url)
            if result:
                result = result.decode("utf-8")
                break
            await asyncio.sleep(0.2)
        return result

    async def delete_result(self, url: str, timeout : int = 10) -> None:
        await asyncio.sleep(timeout)
        self.redis.zrem(self.task_key, url)
        self.redis.hdel(self.result_key, url)

config_task = ConfigTask()

if __name__ == "__main__":
    config_task.add_task("https://main.m.taobao.com/app/ltao-fe/we-detail/home.html?id=673600000000")
    print(config_task.get_task())