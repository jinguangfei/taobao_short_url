import asyncio
import re
import time
import json
import requests
import traceback
import httpx
from typing import Dict, Union

from .config import APIInfo
from ..taobao_tk.service import tk_service
from src.api.utils.taobao_req import crawl, parse_cookie_str


class BaseService(object):
    def __init__(self):
        pass

    def build_url_prev(self, params: APIInfo.Params):
        headers = APIInfo.headers
        headers.update(params.headers)
        _proxies = {
            "http": APIInfo.proxy_url,
            "https": APIInfo.proxy_url,
        }
        proxies = params.proxies or _proxies
        tk_cookie = tk_service.get_taobao_tk()
        cookies = parse_cookie_str(params.cookie+f";{tk_cookie}")
        tk_g = re.search(r"_m_h5_tk=(.*?)_",tk_cookie)
        tk = tk_g.group(1) if tk_g else ""
        return headers, cookies, proxies, tk

    async def _crawl(self, params: APIInfo.Params) -> str:
        headers, cookies, proxies, tk = self.build_url_prev(params)
        data = params.data
        url = params.url
        response = await crawl(url, data, tk, proxies, headers, cookies)
        return response.text if response else ""

    def _check_body(self, body: str) -> str:
        if body.find("mtopjsonp")>-1:
            body = body[body.find("(")+1:-1].replace("({","{",1)
        return body


if __name__ == "__main__":
    service = BaseService()
    cookie = "x5sec=7b22733b32223a2234326236623033656432373833666166222c22617365727665723b33223a22307c43503642756363474550503835376f484d4e4c42355076362f2f2f2f2f77453d227d"
    url = "https://h5api.m.taobao.com/h5/mtop.gaia.nodejs.gaia.arkact.handler/1.0/?jsv=2.7.2&appKey=12574478&t=1760440475865&sign=c80457edb479e6bcb684bbe962c423f7&data="
    data = {"url":"https://huodong.taobao.com/wow/a/act/tao/dailygroup/23509/24308/wupr?wh_pid=daily-557610&disableNav=YES&status_bar_transparent=true&itemId=798527759933","cookie":"hng=CN|zh-CN|CNY|156","device":"pc","backupParams":"device","usePrefetch":"false"}
    proxies = {
    }

    params = APIInfo.Params(cookie=cookie, proxies=proxies, url=url, data=data)
    t = time.time()
    body = asyncio.run(service._crawl(params))
    print(body)
    print(re.findall(r'itemUrl": "//(.*?)"',body))
    print(time.time()-t)