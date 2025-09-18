import asyncio
from re import I
import time
from src.core.redis_script import redis_pool, zpop_min

class Task(object):
    def __init__(self, name : str = "chrome_ext"):
        self.redis = redis_pool
        self.task_key = f"{name}:task"
        self.task_result_key = f"{name}:task:result"

    def add(self, task_id : str) -> None:
        self.redis.zadd(self.task_key, {task_id: int(time.time())})

    def get(self):
        # zpop
        self.redis.zremrangebyscore(self.task_key, 0, int(time.time()) - 10)
        task_id = zpop_min(keys=[self.task_key])
        if task_id:
            task_id = task_id[0].decode("utf-8")
            return task_id

    def over(self, task_id: str, result: str) -> None:
        self.redis.hset(self.task_result_key, task_id, result)

    # 等待timeout秒，获取结果
    async def get_result(self, task_id: str, timeout : int = 10) -> str | None:
        result = None
        start_time = int(time.time())
        while int(time.time()) - start_time < timeout:
            result : bytes = self.redis.hget(self.task_result_key, task_id)
            if result:
                result = result.decode("utf-8")
                break
            await asyncio.sleep(0.2)
        return result

    async def delete(self, task_id: str, timeout : int = 10) -> None:
        await asyncio.sleep(timeout)
        self.redis.zrem(self.task_key, task_id)
        self.redis.hdel(self.task_result_key, task_id)

task = Task()

if __name__ == "__main__":
    task.add("https://main.m.taobao.com/app/ltao-fe/we-detail/home.html?id=673600000000")
    print(task.get())