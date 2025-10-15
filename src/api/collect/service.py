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
    cookie = "sn=;t=f78858d61438e08afa6ee408fcf7f4d8;existShop=MTc2MDUxMTYyNg%3D%3D;cookie1=UUHwg%2FS5WnhNI9amMIJ99KjIP87Gan0TQSnhlgp7604%3D;csg=ad8a19f1;cnaui=2219016869919;wk_cookie2=1c0dea592556bd610f9774d9d9c94133;cookie2=1d3c33ccc166b011ce1980a398fafc72;xlly_s=1;sca=d898b3c8;skt=f395aff6f65c0f82;unb=2219000715303;_tb_token_=e4bbbee853e78;sgcookie=E100xxlDRQjEZdeA6i%2FAfR3epcal4%2FaI7Vfd7wffKaJFaHmg%2FQWLhn1LlpNpZhQ6GGnt%2BAuJLJpYWYtQXZ02Ao24ulUnfEneG702ABkp7WtwkdI%3D;aui=2219016869919;_samesite_flag_=true;tfstk=gA1-LrtGer3Ju9nryM20t0E7nWUD2-bPkg7stHxodiIAqN6kEwtH9MIdv3vQ4QfdDgb1ELbCte1pasXot3qy9wsM9lqgs5bPzQRQjlAf-_U2OeNHA-v7yAggylqgsS2SlBE8jMA0RXvX8nTSNBGQkET9WBTBOpavceLZd0sBOrUvJFLBP3TIcxTH7BtCALaAln8BOUsBOrQX0eToO8KbmhldFuy3_UNkhXGCMUpbnaKjkBfvyCx1P_hIOtTJeh_WDu11pRvd2LC0wc8RhNI2yMPZaQ9dFOO59lFJGNWcVEIQXvKfB_5pI_EtQ31yYGd5HoGJOQ8OJdX0RAKcdZ5vH_ei8E5lR_JM15oWxtbO9eCUYSIOPgB6C_iR421G6a_jjhLnFrUxLvJWuCMuV0ENmKw9kh48yvkeHgLvjrEILvJWuEKgonMELKQc.;wk_unb=UUpgT78RxJVLp%2B1YLw%3D%3D;_cc_=WqG3DMC9EA%3D%3D;thw=cn;x5sec=7b2274223a313736303531313633362c22733b32223a2262373236343065326334363863653066222c22617365727665723b33223a22307c43492b4e76636347454a487a75756a2f2f2f2f2f2f774561447a49794d546b774d4441334d54557a4d444d374d53494b59324677633278705a4756324d6a44357434544741673d3d227d;isg=BKqqAtwUtooWnjrg_B5JfV6h-xZMGy51GWO3WDRjfP2XZ0ghHKmqh6kf85P7l6YN;3PcFlag=1760511617293;_hvn_lgc_=0;_l_g_=Ug%3D%3D;_nk_=tb4268570497;cancelledSubSites=empty;cookie17=UUpgT78RxJVLp%2B1YLw%3D%3D;dnk=tb4268570497;havana_lgc2_0=eyJoaWQiOjIyMTkwMDA3MTUzMDMsInNnIjoiMzA4N2E4MmNkYzEyOGFkNmQ3YjFkMTJmYzM1NjMyOWEiLCJzaXRlIjowLCJ0b2tlbiI6IjFuR1pXN0VfRENfVWpKdmdaNVk1U09BIn0;havana_lgc_exp=1791615628467;havana_sdkSilent=1760540428467;lgc=tb4268570497;sdkSilent=1760540428467;sg=73c;tracknick=tb4268570497;uc1=cookie15=UIHiLt3xD8xYTw%3D%3D&cookie21=Vq8l%2BKCLiw%3D%3D&pas=0&cookie14=UoYY4%2F5MrwyReg%3D%3D&existShop=false&cookie16=VFC%2FuZ9az08KUQ56dCrZDlbNdA%3D%3D;uc3=vt3=F8dD2ky982zq9jjrDe4%3D&nk2=F5RBx%2BY1l9RBu6UP&lg2=Vq8l%2BKCLz3%2F65A%3D%3D&id2=UUpgT78RxJVLp%2B1YLw%3D%3D;uc4=nk4=0%40FY4KoqYDMOMGWq7%2F%2BBtGDXWhDA9nn4Q%3D&id4=0%40U2gqwAAtIxOHqV88D0L5NwuGKiWzCVhO"
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
