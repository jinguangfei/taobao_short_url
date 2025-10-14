import asyncio
import re
import time
import json
import requests
import traceback
import httpx
from typing import Dict, Union

from .config import APIInfo
from src.core.redis_script import redis_pool,zpop_min
from src.loger import logger
from ..base.service import BaseService, APIInfo as BaseAPIInfo


class MiIdService(BaseService):
    def __init__(self):
        super().__init__()
        self.redis = redis_pool
        self.mi_id_key = "mi_id"

    async def crawl(self, params: APIInfo.Params) -> str:
        url = APIInfo.url
        data = {
            "appId":"30986",
            "params":"{\"pageNum\":0,\"pageSize\":25,\"frontAbId\":\"427503\",\"isFirstPage\":true,\"myCna\":\"\"}"
        }
        params = BaseAPIInfo.Params(url=url, data=data, cookie=params.cookie, proxies=params.proxies)
        body = await self._crawl(params)
        return body

    async def crawl_mi_id(self, params: APIInfo.Params) -> str:
        body = await self.crawl(params)
        flag, result = self.check_body(params, body)
        if result:
            self.redis.zadd(self.mi_id_key, result)
        logger.info(f"crawl mi_id {len(result)} {self.redis.zcard(self.mi_id_key)}")
        return result

    async def get_mi_id(self, params: APIInfo.Params) -> str:
        if params.real_time:
            result = await self.crawl_mi_id(params)
            mi_id = result.popitem()[0] if result else ""
        else:
            mi_id = self._get_mi_id()
            if not mi_id:
                result =await self.crawl_mi_id(params)
                mi_id = self._get_mi_id()
        return mi_id

    def _get_mi_id(self, add_t : int = 60 * 5) -> str:
        mi_id = ""
        try:
            self.redis.zremrangebyscore(self.mi_id_key, 0, int(time.time())-add_t)
            mi_id, t = zpop_min(keys=[self.mi_id_key])
            if mi_id:
                return mi_id.decode()
        except Exception as e:
            logger.error(f"get mi_id error {e}")
        return mi_id

    def check_body(self, params: APIInfo.Params, body: str) -> tuple[str, str]:
        body = self._check_body(body)

        mi_id_g = re.findall(r"mi_id=(.*?)\"",body)
        all_result = mi_id_g if mi_id_g else []
        result = {i:int(time.time()) for i in all_result}
        return "success", result

if __name__ == "__main__":
    service = MiIdService()
    cookie = ""
    params = APIInfo.Params(cookie=cookie, proxies={})
    body = asyncio.run(service.crawl_mi_id(params))
    mi_id = service.get_mi_id()
    print(mi_id)
