import asyncio
import random
from src.core.redis_script import redis_pool
from src.loger import logger

class DamaiCookieService(object):
    def __init__(self):
        self.redis = redis_pool
        self.logger = logger
        self.flag_key = "damai:cookie:flag"
        self.cookie_key = "damai:cookie"

    async def get_cookie(self) -> str:
        cookie = self.redis.get(self.cookie_key)
        if not cookie:
            self.redis.set(self.flag_key, 1, ex=60*2)
            for i in range(10):
                cookie = self.redis.get(self.cookie_key)
                if cookie:
                    break
                await asyncio.sleep(0.3)
        if isinstance(cookie, bytes):
            cookie = cookie.decode("utf-8")
        return cookie

if __name__ == "__main__":
    service = DamaiCookieService()
    print(asyncio.run(service.get_cookie()))