import asyncio
import re
import random
import time
import json
import requests
import traceback
import httpx
from curl_cffi.requests import AsyncSession
from typing import Dict, Union

from .config import APIInfo
from ..taobao_tk.service import TaobaoTkService
from src.core.redis_script import redis_pool
from src.api.utils.taobao_req import crawl, parse_cookie_str

class CollectService(object):
    def __init__(self):
        self.redis = redis_pool
        self.api_info = APIInfo
        self.taobao_tk_service = TaobaoTkService()

    async def build_url_prev(self, params: APIInfo.Params):
        headers = self.api_info.headers
        _proxies = {
            "http": APIInfo.proxy_url,
            "https": APIInfo.proxy_url,
        }
        _proxies = {}
        proxies = params.proxies or _proxies
        tk_cookie = self.taobao_tk_service.get_taobao_tk()
        cookies = parse_cookie_str(params.cookie+f";{tk_cookie}")
        tk_g = re.search(r"_m_h5_tk=(.*?)_",tk_cookie)
        tk = tk_g.group(1) if tk_g else ""
        return headers, cookies, proxies, tk

    async def collect_url(self, params: APIInfo.Params, **kwargs):
        headers, cookies, proxies, tk = await self.build_url_prev(params)
        data = {
            "itemId":params.targetId,
            "type":"1",
            "appName":"detailH5",
        }
        return await crawl(self.api_info.collect_url, data, tk, proxies, headers, cookies)

    async def item_list_url(self, params: APIInfo.Params, **kwargs):
        headers, cookies, proxies, tk = await self.build_url_prev(params)
        data = {
            "itemType":1,
            "platformCode":0,
            "appName":"favorite",
            "pageSize":50,
            "pageNum":0,
            "startTime":"0",
            "weexVersion":2
        }
        return await crawl(self.api_info.item_list_url, data, tk, proxies, headers, cookies, **kwargs)

    def _check_body(self, body: str) -> str:
        if body.find("mtopjsonp")>-1:
            body = body[body.find("(")+1:-1].replace("({","{",1)
        return body

    def check_collect_body(self, params: APIInfo.Params, body: str) -> tuple[str, str]:
        body = self._check_body(body)

        flag, result = "success", None
        recv_dict : Dict = json.loads(body)
        if recv_dict.get("ret",[]).find("SUCCESS::收藏成功")>-1:
            flag = "success"
        elif recv_dict.get("ret",[]).find("FAIL_SYS_SESSION")>-1:
            flag = "login"
        elif recv_dict.get("ret",[]).find("RGV587_ERROR")>-1:
            flag = "deny"
        else:
            flag = "failed"
        return flag, result

    def check_item_list_body(self, params: APIInfo.Params, body: str) -> tuple[str, str]:
        body = self._check_body(body)
        flag, result = "success", None

        login_flag = body.find("session")>-1 or body.find("login.htm")>-1
        deny_flag = body.find("pureDenyWait")>-1
        if login_flag:
            flag = "login"
        elif deny_flag:
            flag = "deny"
        else:
            flag = "success"

        recv_dict : Dict = json.loads(body)
        item_list = recv_dict.get("data",{}).get("favList",[])
        result = [i.get("favId")+" "+i.get("itemUrl") for i in item_list]
        return flag, result

if __name__ == "__main__":
    service = CollectService()
    cookie = "sn=;t=f78858d61438e08afa6ee408fcf7f4d8;existShop=MTc2MDUzMDA3MA%3D%3D;cookie1=UUHwg%2FS5WnhNI9amMIJ99KjIP87Gan0TQSnhlgp7604%3D;csg=957741cf;cnaui=2219000715303;wk_cookie2=1c0dea592556bd610f9774d9d9c94133;cookie2=1d3c33ccc166b011ce1980a398fafc72;xlly_s=1;sca=d898b3c8;skt=30b6c48c7cbbfb98;unb=2219000715303;_tb_token_=e4bbbee853e78;sgcookie=E100CSpqZgFVz%2B6CU%2BSU0uEOSWA4UFqFJRGMAqW0AQhSsMwU%2B1L5FnpzqO188fi0VAb2KCwWgLN8G87N2DO5h%2Bl%2BdDZH3PWAmIsMHq9PJ6we1Es%3D;aui=2219000715303;_samesite_flag_=true;tfstk=g9S-I0AGy-H-QsGre640xYnMC3w0jrXrk_WsxBAoRsCACOlkRB4P9eChgeskqTfAdOXFtT2e-HIdsIfnxTfnUZ5GC0juzHmp4H-Qs5qgjYWyYHgFGfT6at62d-vShv_vQH-QsSqgjTWyY_ODW5ISlKO2pp9BP66bHLRjVpiWdjwvLItBAH1CuHIvGBtBA66bHpRXOHtBypzJGSAZvaNohIKVwInIAip7TC6JMKJVDLLJ1lRxvYSveUd1FGdPsBvd5GLP1S0kNNQh6dfuc0COF_Q65gGbMHWcW6pOVRg99_WfqEs7KVJ2Ya_6VMFtNt8OcgxPk5nM1ZWCvE6z6VJcROjlJ_VqAQbOhsLGmjmMcgCRVEK14csGXT6jsCpny-ex828W3hguNbngeTdpHC28e2uek_pvs-FI828W3KdgnIgE8EBc.;wk_unb=UUpgT78RxJVLp%2B1YLw%3D%3D;_cc_=Vq8l%2BKCLiw%3D%3D;thw=cn;_m_h5_tk_enc=7db929fedef851bc59cc12fb714b16ea;isg=BO_vsh8F24lDvN-zaWG0HrP2fgX5lEO25BRS6wF8jN5lUA9SCWCxBgCS0EDuMxsu;3PcFlag=1760530045196;_hvn_lgc_=0;_l_g_=Ug%3D%3D;_m_h5_tk=b15bb36d7ae8e0d0da613e8a348e0967_1760535198307;_nk_=tb4268570497;cancelledSubSites=empty;cookie17=UUpgT78RxJVLp%2B1YLw%3D%3D;dnk=tb4268570497;havana_lgc2_0=eyJoaWQiOjIyMTkwMDA3MTUzMDMsInNnIjoiNmMxNzdjMzY4MTlkZTgyMjI5OTg1MTFiYzE2ODE5NDYiLCJzaXRlIjowLCJ0b2tlbiI6IjEyeTlxT3owWWVnQUVEZEhzMlRjbl93In0;havana_lgc_exp=1791634070050;havana_sdkSilent=1760540428467;lgc=tb4268570497;sdkSilent=1760540428467;sg=73c;tracknick=tb4268570497;uc1=cookie21=VFC%2FuZ9ajQ%3D%3D&cookie15=Vq8l%2BKCLz3%2F65A%3D%3D&cookie16=URm48syIJ1yk0MX2J7mAAEhTuw%3D%3D&cookie14=UoYY4%2F5O5euVfA%3D%3D&pas=0&existShop=false;uc3=id2=UUpgT78RxJVLp%2B1YLw%3D%3D&lg2=UIHiLt3xD8xYTw%3D%3D&nk2=F5RBx%2BY1l9RBu6UP&vt3=F8dD2ky98Y%2B9l5Wu7OA%3D;uc4=nk4=0%40FY4KoqYDMOMGWq7%2F%2BBtGDXWhDg%2F2SNM%3D&id4=0%40U2gqwAAtIxOHqV88D0L5NwuGKicEEPvv"
    with open("src/tmp/t3","r") as f:
        item_id_list = f.readlines()
        item_id_list = [i.strip() for i in item_id_list]
    params = APIInfo.Params(targetId="", cookie=cookie, proxies={})
    res = asyncio.run(service.item_list_url(params))
    flag, result = service.check_item_list_body(params=params,body=res.text)
    with open("src/tmp/t4","a") as f:
        f.write("\n".join(result)+"\n")
    with open("src/tmp/t4","r") as f:
        have_list = f.readlines()
        have_list = [i.strip() for i in have_list]
        have_id_list = {i.split(" ")[0] for i in have_list}
    print(len(item_id_list))
    item_id_list = [i for i in item_id_list if i not in have_id_list]
    print(len(item_id_list))
    for i in range(10):
        for item_id in item_id_list[20*i:20*(i+1)]:
            params = APIInfo.Params(targetId=item_id, cookie=cookie, proxies={})
            res = asyncio.run(service.collect_url(params))
            print(res.text)
            time.sleep(8)
        res = asyncio.run(service.item_list_url(params))
        flag, result = service.check_item_list_body(params=params,body=res.text)
        with open("src/tmp/t4","a") as f:
            f.write("\n".join(result)+"\n")
        print(flag, len(result))
