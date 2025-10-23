import asyncio
import time
from tortoise.expressions import Q
from curl_cffi.requests import AsyncSession
from curl_cffi.requests.models import Response

from src.core.redis_script import redis_pool
from src.loger import logger
from src.core.zhihai_queue import MyQueue

my_queue = MyQueue("shanchen")
async def get_proxies() -> dict:
    recv_dict = await my_queue.get_one_info(add_t=20)
    print(recv_dict)
    if not recv_dict:
        proxies = {}
    else:
        proxies = {
            "http": f"http://{recv_dict.get('proxy_ip')}:{recv_dict.get('proxy_port')}",
            "https": f"http://{recv_dict.get('proxy_ip')}:{recv_dict.get('proxy_port')}",
        }
    return proxies

class XianyuCookieService(object):
    def __init__(self):
        self.redis = redis_pool
        self.redis_key = "source:flag"

    async def get_first_need(self) -> dict:
        cur_t = int(time.time())
        url = "http://127.0.0.1:8000/api/source/list?name=xianyu_cookie&status=1&expire_time=60&&order=init_t"
        async with AsyncSession() as session:
            response = await session.get(url)
            recv_dict =response.json()
            print(recv_dict)
        if recv_dict["code"] == 200 and recv_dict["total"] > 0:
            return recv_dict["data"][0]
        return None

    async def get_new_cookies(self, cookie: str) -> str:
        url = "http://127.0.0.1:8000/api/xianyu_cookie/relogin"
        proxies = await get_proxies()
        data = {
            "cookie_str": cookie,
            "proxies": proxies
        }
        async with AsyncSession() as session:
            response = await session.post(url, json=data)
            print(response.text)

    async def run(self):
        while True:
            flag = self.redis.hget(self.redis_key, "xianyu_cookie")
            cur_t = int(time.time())
            if flag and int(flag) > cur_t - 3: # 5秒内有获取资源但是 没有取到的情况
                source = await self.get_first_need()
                if source:
                    cookie = source["value"]
                    await self.get_new_cookies(cookie)
            await asyncio.sleep(1)

if __name__ == "__main__":
    service = XianyuCookieService()
    asyncio.run(service.run())