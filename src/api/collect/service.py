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
        result = [i.get("itemUrl") for i in item_list]
        return flag, result

if __name__ == "__main__":
    service = CollectService()
    cookie = "mtop_partitioned_detect=1;_m_h5_tk=d6fdeaf0d7c9231481448aa8b57ead0f_1759681517947;_m_h5_tk_enc=066ded208f5e00ae5cec92c67e572da7;XSRF-TOKEN=9a7a6c68-6b33-44f7-9b40-d5b90a4ae663;_samesite_flag_=true;cookie2=162c11bd62c0ef21dcc90934df8358b7;t=72a52205ee19b3727c8351ae2e50c3e3;_tb_token_=ed7134735e305;cbc=;JSESSIONID=XEF66QB1-8H6ZK0ARAWJU76BQU0AM3-XSQ5RDGM-XSY7;ivActionType=pc_login_check;tmp0=CjeTRP%2FMhsEzWYPp%2FDx4GLk%2Bgi8%2BIPIVroHmglKS8AH%2BMLcKH%2B1bTzzDhsnTdaG5lzL%2B6RHJm2%2B5i%2BHWh9aVV8XC1nmZbjRgPas01NTzEA7pEPo0YeYRnvIr8EJCGAZqRfd9sIuveQ%2FmvHDA7R%2BquA%3D%3D;siv20=nlRyzPBC%2B0Zkqp0uOcKJKYKXMcZvIq%2FsHw%2BUbiL%2FyOmn9kLr64JicyyQA5Sl3AOuGtNUWIm3QxGuu0dgG96FIJIvXPKFfwqGPPhxGk5hATEesKLw0CYz3mLHdlIFUMsD;sgcookie=E100rOjuLlLd5eSxfFe8OeXqHaL3FecSgdzaDZ9h3E4RZCf5%2B%2BWhciqQQDLMluWz7JdDYWZE8VMFnhuJBvv67KdpqVZ38YeWQgBvqxEQPdkpFw4%3D;wk_cookie2=121a35efc7174d3c8a8f4aef247c28b6;wk_unb=UUpgT71fEVt7wiR2lQ%3D%3D;unb=2219205148160;uc1=cookie15=Vq8l%2BKCLz3%2F65A%3D%3D&existShop=false&cookie21=UIHiLt3xTIkz&cookie14=UoYbwhdvnQiJ7w%3D%3D&pas=0&cookie16=VT5L2FSpNgq6fDudInPRgavC%2BQ%3D%3D;sn=;uc3=vt3=F8dD2k07K46Crju%2BDPA%3D&id2=UUpgT71fEVt7wiR2lQ%3D%3D&nk2=F5RBxrZ6EeRUMerbWPc%3D&lg2=Vq8l%2BKCLz3%2F65A%3D%3D;csg=901ebbb0;ultraCookieBase=;lgc=tb430820765434;cancelledSubSites=empty;cookie17=UUpgT71fEVt7wiR2lQ%3D%3D;dnk=tb430820765434;skt=bd83637f2ffa04ed;existShop=MTc1OTY3MTgxNA%3D%3D;uc4=nk4=0%40FY4Ko%2BO1pBDUpKJJtLprSdZapxQT8ItXJQ%3D%3D&id4=0%40U2gqwAJDDhoJ%2FKo2xrHMW79DQ%2FjOAGoU;publishItemObj=;tracknick=tb430820765434;lc=V3oSBtpTigM6GSjpXWshHnpE6A%3D%3D;_cc_=UIHiLt3xSw%3D%3D;lid=tb430820765434;_l_g_=Ug%3D%3D;sg=400;_nk_=tb430820765434;cookie1=BdLU8kEmmWgM44CyitgC%2FKBJEzmWqRuqvZMbJJvR1y4%3D"
    item_id_list = ["965108563706","751814603817","10447525582","818866392239","876211246588","834550783063","777385071865","672467520722","864256925532","575148883140","597793354025","903636308905","547824223246","887247116971","674429724595","853122926019","661502754299","961668382336","745102606911","669670189609","628185360446","913976882481","583568298676","632978203677","778660455681","724638296478","614446707152","743846854913","666520398271","930084849983","790307245012","624312389961","860191995216","886392736471","910329177073","563351406678","889011383928","640853425712","723817544443","612906917177","898483367470","720279697515","657507942118","790570318410","671373851603","551388183855","616658456697","832824272732","714894672792","861968569418","727760709607","766142177523","862619170830","637586103814","698883133374","740744526711","926379519273","598358687603","884906702961","730177795324","644892039623","705058472150","550382355744","675076563209","595354917876","712745738555","683105787795","912738171978","626301988342","627147263711","926305281632","822273860843","682898120157","828353218044","770409757961","742855061590","842001352921","941190365257","844479922433","849520821455","688932446802","822150377419","772362660612","785499774448","818135118849","950984136695","684563539010","842249701429","717555744763","682231880696","593232961703","708570743299","902881384191","558659288784","681497540116","42534924619","691587176886","782082364301","628044230924","642279545295"]
    params = APIInfo.Params(targetId="", cookie=cookie, proxies={})
    for item_id in item_id_list[::-1]:
        item_id = "680686125578"
        params = APIInfo.Params(targetId=item_id, cookie=cookie, proxies={})
        res = asyncio.run(service.collect_url(params))
        print(res.text)
        res = asyncio.run(service.item_list_url(params))
        print(res.text)
        flag, result = service.check_item_list_body(params=params,body=res.text)
        print(flag, len(result))
        time.sleep(8)
        break

