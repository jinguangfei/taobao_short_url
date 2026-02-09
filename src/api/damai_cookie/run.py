import sys
import asyncio
import time
from tortoise.expressions import Q
from curl_cffi.requests import AsyncSession
from curl_cffi.requests.models import Response

from src.core.redis_script import redis_pool
from src.loger import logger
from .service import DamaiReloginService
login_service= DamaiReloginService()

class DamaiCookieService(object):
    def __init__(self):
        self.redis = redis_pool
        self.name = "damai_cookie"
        self.redis_key = "source:flag"

    async def get_first_need(self, status: int = 1, expire_time: int = 10) -> dict:
        cur_t = int(time.time())
        url = f"http://123.56.44.124:9460/api/source/list?name={self.name}&status={status}&expire_time={expire_time}&&order=init_t"
        async with AsyncSession() as session:
            response = await session.get(url)
            recv_dict =response.json()
            print(recv_dict)
        if recv_dict["code"] == 200 and recv_dict["total"] > 0:
            return recv_dict["data"][0]
        return None

    async def get_new_cookies(self, times : int = 5) -> str:
        for i in range(times):
            flag, cookie_str = await service.get_new_cookies()
            if cookie_str:
                break

    async def run(self):
        while True:
            flag = self.redis.hget(self.redis_key, self.name)
            cur_t = int(time.time())
            if flag and int(flag) > cur_t - 3: # 5秒内有获取资源但是 没有取到的情况
                await login_service.get_new_cookies()
            await asyncio.sleep(1)

if __name__ == "__main__":
    service = DamaiCookieService()
    asyncio.run(service.run())