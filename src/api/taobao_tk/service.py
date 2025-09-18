import asyncio
import random
from src.core.redis_script import get_redis_pool, RedisSettings
from src.loger import logger
redis_settings = RedisSettings()
redis_settings.REDIS_DB = 6

class TaobaoTkService(object):
    def __init__(self):
        self.redis_pool = get_redis_pool(redis_settings)
        self.logger = logger
        self.table_name = "taobao_bx_cookie"

    async def get_taobao_tk(self) -> str:
        while True:
            results = self.redis_pool.zrange(self.table_name, 0, 10)
            if results: 
                tk = random.choice(results).decode("utf-8")
                return tk
            await asyncio.sleep(1)

if __name__ == "__main__":
    service = TaobaoTkService()
    print(asyncio.run(service.get_taobao_tk()))