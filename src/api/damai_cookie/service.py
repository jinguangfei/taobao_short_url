import json 
import asyncio
import traceback
from curl_cffi.requests import AsyncSession
from curl_cffi.requests.models import Response
from typing import Dict, Tuple
from enum import Enum
import time
from src.core.redis_script import redis_pool
from src.loger import logger
from .config import APIInfo
from src.api.source.service import source_controller
from src.api.source.schemas import SourceCreate
from src.api.utils.func import parse_cookie_str, parse_set_cookies, get_x5sec
from pydantic import BaseModel


class ReloginFlag(Enum):
    SUCCESS = "success"
    FAIL = "fail"
    TIMEOUT = "timeout"

class DamaiReloginService(object):
    def __init__(self, name : str = "damai_cookie"):
        self.name = name
        self.redis = redis_pool
        self.x5sec_redis_key = "dm:login:x5sec"

    async def get_new_cookies(self, check_flag = lambda x: x and "sgcookie" in x) -> Tuple[ReloginFlag, str]:
        flag, cookie_str = await self._get_new_cookies(check_flag)
        cookies = parse_cookie_str(cookie_str)
        login_id = cookies.get("munb")
        status = 1 if flag == ReloginFlag.SUCCESS else 0
        source_create = SourceCreate(
            name=self.name,
            uniq_id=login_id,
            value=cookie_str,
            init_t=int(time.time()),
            use_t=0,
            status=status
        )
        url = "http://123.56.44.124:9460/api/source/create"
        async with AsyncSession() as session:
            response : Response = await session.post(url, json=source_create.model_dump())
            print(response.json())

        logger.info(f"login_id {login_id} relogin {flag.value}")
        return flag, cookie_str

    async def _get_new_cookies(self, check_flag = lambda x: "sgcookie" in x) -> Tuple[ReloginFlag, str]:
        """执行登录状态检查请求"""
        # 请求URL
        url = f'http://123.56.44.124:9464/api/ext_call/?name=damai_login&phone_num=1&passwd=1&batch={int(time.time())}&timeout=10'
        # 请求头
        headers = {
        }
        
        flag = ReloginFlag.FAIL
        cookie_str = ""
        try:
            async with AsyncSession() as session:
                response : Response = await session.get(url, headers=headers)
            cookie_str = response.json().get("data")
            flag = ReloginFlag.SUCCESS if check_flag(cookie_str) else ReloginFlag.FAIL
        except Exception as e:
            logger.error(f"relogin error: {traceback.format_exc()}")
            flag = ReloginFlag.TIMEOUT
        return flag, cookie_str

if __name__ == "__main__":
    service = DamaiReloginService()
    flag, cookie_str = asyncio.run(service._get_new_cookies())
    print(cookie_str)