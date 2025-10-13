import asyncio
import re
import time
import json
import requests
import traceback
import httpx
from typing import Dict, Union

from .config import APIInfo
from ..utils import parse_url, md5_data
from ..taobao_tk.service import TaobaoTkService

from src.core.redis_script import redis_pool,zpop_min
from src.loger import logger


class MiIdService(object):
    def __init__(self):
        self.redis = redis_pool
        self.api_info = APIInfo
        self.taobao_tk_service = TaobaoTkService()
        self.mi_id_key = "mi_id"

    def parse_cookie_str(self, cookie_str : str) -> dict:
        cookie_dict = {i.split("=")[0]:i.split("=",1)[1] for i in cookie_str.replace("; ",";").split(";") if len(i.split("="))>1}
        return cookie_dict

    async def build_url(self, params: APIInfo.Params):
        headers = self.api_info.headers
        _proxies = {
            "http": "http://LVMJTEaf:XW2zzQtS@122.228.200.202:19258",
            "https": "http://LVMJTEaf:XW2zzQtS@122.228.200.202:19258",
        }
        proxies = params.proxies or _proxies
        url , query_params = parse_url(self.api_info.url)
        tk_cookie = await self.taobao_tk_service.get_taobao_tk()
        cookies = self.parse_cookie_str(params.cookie+f";{tk_cookie}")

        data = {
        }
        data_str = json.dumps(data).replace(" ", "")
        data_str = query_params.get("data")

        tk_g = re.search(r"_m_h5_tk=(.*?)_",tk_cookie)
        tk = tk_g.group(1) if tk_g else ""

        t, sign, data_str = md5_data(tk, data_str, app_key="12574478")
        query_params["data"] = data_str
        query_params["sign"] = sign
        query_params["t"] = t

        return url, query_params, headers, cookies, proxies

    def get_mi_id(self, add_t : int = 60 * 5) -> str:
        mi_id = ""
        try:
            self.redis.zremrangebyscore(self.mi_id_key, 0, int(time.time())-add_t)
            mi_id, t = zpop_min(keys=[self.mi_id_key])
            if mi_id:
                return mi_id.decode()
        except Exception as e:
            logger.error(f"get mi_id error {e}")
        return mi_id

    async def crawl(self, params: APIInfo.Params) -> str:
        url, query_params, headers, cookies, proxies = await self.build_url(params)
        try:
            res = requests.get(url, headers=headers, params=query_params, timeout=10, cookies=cookies, proxies=proxies)
            flag, result = self.check_body(params, res.text)
            if result:
                self.redis.zadd(self.mi_id_key, result)
            logger.info(f"crawl mi_id {len(result)} {self.redis.zcard(self.mi_id_key)}")
        except Exception as e:
            return ""

    def _check_body(self, body: str) -> str:
        if body.find("mtopjsonp")>-1:
            body = body[body.find("(")+1:-1].replace("({","{",1)
        return body

    def check_body(self, params: APIInfo.Params, body: str) -> tuple[str, str]:
        body = self._check_body(body)

        mi_id_g = re.findall(r"mi_id=(.*?)\"",body)
        all_result = mi_id_g if mi_id_g else []
        result = {i:int(time.time()) for i in all_result if i.find("000")==0}
        return "success", result

if __name__ == "__main__":
    service = MiIdService()
    cookie = ""
    params = APIInfo.Params(cookie=cookie, proxies={})
    asyncio.run(service.crawl(params))
    print(service.get_mi_id())