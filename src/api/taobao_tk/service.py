import time
import asyncio
import random
from src.core.redis_script import get_redis_pool, RedisSettings
redis_settings = RedisSettings()
redis_settings.REDIS_DB = 6

class TaobaoTkService(object):
    def __init__(self):
        self.redis_pool = get_redis_pool(redis_settings)
        self.table_name = "taobao_bx_cookie"

    def get_taobao_tk(self) -> str:
        while True:
            results = self.redis_pool.zrange(self.table_name, 0, 10)
            if results: 
                tk = random.choice(results).decode("utf-8")
                return tk
            time.sleep(1)
        
tk_service = TaobaoTkService()

if __name__ == "__main__":
    service = TaobaoTkService()
    print(service.get_taobao_tk())