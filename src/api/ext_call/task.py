import os
import asyncio
from typing import List
import time
from src.core.redis_script import redis_pool, zpop_min

class Task(object):
    def __init__(self, name : str = "chrome_ext"):
        self.redis = redis_pool
        self.task_key = f"{name}:task" + ":{name}"
        self.task_result_key = f"{name}:task" + ":{name}:result"

        # 创建data目录
        self.data_dir = f"data/{name}"
        if not os.path.exists(self.data_dir):
            os.makedirs(self.data_dir)




    def add(self, name : str, task_id : str) -> None:
        task_key = self.task_key.format(name=name)
        self.redis.zadd(task_key, {task_id: int(time.time())})

    def get(self, name : str):
        task_key = self.task_key.format(name=name)
        # zpop
        self.redis.zremrangebyscore(task_key, 0, int(time.time()) - 10)
        task_id : List[bytes] = zpop_min(keys=[task_key])
        if task_id:
            task_id = task_id[0].decode("utf-8")
            return task_id

    def over(self, name : str, task_id: str, result: str) -> None:
        task_result_key = self.task_result_key.format(name=name)
        #self.redis.hset(task_result_key, task_id, result)
        with open(f"{self.data_dir}/{task_id}", "w") as f:
            f.write(result)

    # 等待timeout秒，获取结果
    async def get_result(self, name : str, task_id: str, timeout : int = 10) -> str | None:
        task_result_key = self.task_result_key.format(name=name)
        result = None
        start_time = int(time.time())
        while int(time.time()) - start_time < timeout:
            #result : bytes = self.redis.hget(task_result_key, task_id)
            with open(f"{self.data_dir}/{task_id}", "r") as f:
                result = f.read()
            if result:
                break
            await asyncio.sleep(0.2)
        return result

    async def delete(self, name : str, task_id: str, timeout : int = 10) -> None:
        await asyncio.sleep(timeout)
        task_key = self.task_key.format(name=name)
        self.redis.zrem(task_key, task_id)
        task_result_key = self.task_result_key.format(name=name)
        self.redis.hdel(task_result_key, task_id)

    async def delete_task(self, name : str, task_id: str, timeout : int = 10) -> None:
        await asyncio.sleep(timeout)
        task_key = self.task_key.format(name=name)
        self.redis.zrem(task_key, task_id)

    async def delete_result(self, name : str, task_id: str, timeout : int = 10) -> None:
        await asyncio.sleep(timeout)
        task_result_key = self.task_result_key.format(name=name)
        self.redis.hdel(task_result_key, task_id)

task = Task()

if __name__ == "__main__":
    task.add("crawl", "https://main.m.taobao.com/app/ltao-fe/we-detail/home.html?id=673600000000")
    print(task.get("crawl"))