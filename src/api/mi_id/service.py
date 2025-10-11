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


class MiIdService(object):
    def __init__(self):
        self.api_info = APIInfo
        self.taobao_tk_service = TaobaoTkService()

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
        print(query_params)
        data_str = json.dumps(data).replace(" ", "")
        data_str = query_params.get("data")

        tk_g = re.search(r"_m_h5_tk=(.*?)_",tk_cookie)
        tk = tk_g.group(1) if tk_g else ""
        print(tk)
        print(cookies)

        t, sign, data_str = md5_data(tk, data_str, app_key="12574478")
        query_params["data"] = data_str
        query_params["sign"] = sign
        query_params["t"] = t

        return url, query_params, headers, cookies, proxies

    async def crawl(self, params: APIInfo.Params) -> str:
        url, query_params, headers, cookies, proxies = await self.build_url(params)
        try:
            res = requests.get(url, headers=headers, params=query_params, timeout=10, cookies=cookies, proxies=proxies)
            return res.text
        except Exception as e:
            print(traceback.format_exc())
            return ""

    def _check_body(self, body: str) -> str:
        if body.find("mtopjsonp")>-1:
            body = body[body.find("(")+1:-1].replace("({","{",1)
        return body

    def check_body(self, params: APIInfo.Params, body: str) -> tuple[str, str]:
        body = self._check_body(body)

        flag = "success"
        mi_id_g = re.search(r"mi_id=(.*?)\"",body)
        result = mi_id_g.group(1) if mi_id_g else ""
        return flag, result

if __name__ == "__main__":
    service = MiIdService()
    cookie = ""
    params = APIInfo.Params(cookie=cookie, proxies={})
    body = asyncio.run(service.crawl(params))
    flag, result = service.check_body(params, body)
    print(flag, result)