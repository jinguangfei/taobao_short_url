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
from ..utils import parse_url, md5_data
from ..taobao_tk.service import TaobaoTkService
from src.core.redis_script import redis_pool



class CollectService(object):
    def __init__(self):
        self.redis = redis_pool
        self.api_info = APIInfo
        self.taobao_tk_service = TaobaoTkService()

    def parse_cookie_str(self, cookie_str : str) -> dict:
        cookie_dict = {i.split("=")[0]:i.split("=",1)[1] for i in cookie_str.replace("; ",";").split(";") if len(i.split("="))>1}
        return cookie_dict

    async def build_url_prev(self, params: APIInfo.Params):
        headers = self.api_info.headers
        _proxies = {
            "http": "http://LVMJTEaf:XW2zzQtS@122.228.200.202:19258",
            "https": "http://LVMJTEaf:XW2zzQtS@122.228.200.202:19258",
        }
        _proxies = {}
        proxies = params.proxies or _proxies
        tk_cookie = await self.taobao_tk_service.get_taobao_tk()
        cookies = self.parse_cookie_str(params.cookie+f";{tk_cookie}")
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
        return await self.crawl(self.api_info.collect_url, data, tk, proxies, headers, cookies, **kwargs)

    async def crawl(self, url: str, data: dict, tk: str, proxies: dict, headers: dict, cookies: dict, **kwargs):
        url, query_params = parse_url(url)
        data_str = json.dumps(data).replace(" ", "")
        t, sign, data_str = md5_data(tk, data_str, app_key="12574478")
        query_params["data"] = data_str
        query_params["sign"] = sign
        query_params["t"] = t
        try:
            async with AsyncSession() as session:
                res = await session.get(url, headers=headers, params=query_params, timeout=10, cookies=cookies, proxies=proxies)
            return res.text
        except Exception as e:
            print(traceback.format_exc())
            return ""

    
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
        return await self.crawl(self.api_info.item_list_url, data, tk, proxies, headers, cookies, **kwargs)

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
    cookie = "_samesite_flag_=true;3PcFlag=1760350317162;cookie2=1551d538c954b629133aa22bef9e3913;t=bd7cd1833029adad6a846afe487efc34;_tb_token_=e6ae1b7ede59e;cna=b75zITO0x3oCAdpKXuj2rP7J;xlly_s=1;unb=2220982881300;lgc=tb945232807697;cancelledSubSites=empty;cookie17=UUpjNmpDKmtwbsDP3w%3D%3D;dnk=tb945232807697;tracknick=tb945232807697;_l_g_=Ug%3D%3D;sg=705;_nk_=tb945232807697;cookie1=BYb7hAwLWSDgC%2BNSYdy4q66m84jylapYzsUd33U39IE%3D;sgcookie=E100iaEi%2FC7CcMDA4l9IYnAQ2ZUt%2FHOJilo3RBrt%2BnFFH%2Bi2XS2kJddt%2B6Qe4DuyAaBhFc7Ww3JaZRzBsoEyeXNA2Garzq0XCFNYAot4%2FInOdfU%3D;havana_lgc2_0=eyJoaWQiOjIyMjA5ODI4ODEzMDAsInNnIjoiZWIwYmNmZjc2ZDFhNjI3ZDUxOWY0MWZlN2UxOGE2NzAiLCJzaXRlIjowLCJ0b2tlbiI6IjE1YXhWS2lRYVFQeFVzcWJMaGp5eHBRIn0;_hvn_lgc_=0;cookie3_bak=1551d538c954b629133aa22bef9e3913;cookie3_bak_exp=1760609987187;sn=;uc3=id2=UUpjNmpDKmtwbsDP3w%3D%3D&lg2=Vq8l%2BKCLz3%2F65A%3D%3D&vt3=F8dD2k0wPVx78mZcGVM%3D&nk2=F5RMHUF1jOLLQ0uaUok%3D;csg=53ce1123;env_bak=FM%2Bgm%2FLsIHl9KxTD7W74a%2BkU%2B8KFIA0kRpDxVqL1lum7;skt=83a044665aa1ae3a;existShop=MTc2MDM1MDc4Nw%3D%3D;uc4=id4=0%40U2gp9rlpStQpwEFnUrnbpU6H8eOF5A3d&nk4=0%40FY4HWGscRJjr%2FxHtgiYmawmuT0HdjyNDLw%3D%3D;_cc_=UIHiLt3xSw%3D%3D;uc1=cookie16=WqG3DMC9UpAPBHGz5QBErFxlCA%3D%3D&cookie15=W5iHLLyFOGW7aA%3D%3D&pas=0&cookie21=W5iHLLyFfoaZ&cookie14=UoYY4%2FiA8tDbPw%3D%3D&existShop=false;havana_lgc_exp=1791454801456;sdkSilent=1760379601456;havana_sdkSilent=1760379601456;_m_h5_tk=7d0e77d257092d91bbfcb1cee061852e_1760358076750;_m_h5_tk_enc=558024528cda3b80a374779e04c6f84c;aui=2220982881300;sca=c4f5ae44;thw=cn;tfstk=gPeoGVYDN7l5a8pWZMD5wIAhMK1YVYMIwypKJv3FgqujwgN8vS2nolSSy617-S4Ulb3zKk9nYkzCV2I5MuZSdv7OWeXTVuw_2xllkvSU0vn3cE9eKuZSdn_OWOBTVHYX9qrrY2Sm3Dmn8vorYiAqbqJrYLoeuimIuvkELyPjK-0q8vkU8oSmAquELvkwv3uaLWyV8dodI3dvM-moZVvZopvhv0co7uumcmwqdb0a4qvFzwY5X20bQZC0cSVzymahIZDQlWzExr8VJbZUirmuyNYIJ8Z8KmZlaZZSES2me87B1oEm8yDUNMT4DP3u_YZpAZrmslNKgjQwt2l_m8lZLHp3RYgre8cvkCZmhqkmcJQXU2V4T8hSdU7tNkP0o0DN4ER2_dWJdVB0ABOIamimWqNFcHkqnYNfmiA_ObojjVIcmBOIamimWijD9chrcmfl."
    item_id_list = ["965108563706","751814603817","10447525582","818866392239","876211246588","834550783063","777385071865","672467520722","864256925532","575148883140","597793354025","903636308905","547824223246","887247116971","674429724595","853122926019","661502754299","961668382336","745102606911","669670189609","628185360446","913976882481","583568298676","632978203677","778660455681","724638296478","614446707152","743846854913","666520398271","930084849983","790307245012","624312389961","860191995216","886392736471","910329177073","563351406678","889011383928","640853425712","723817544443","612906917177","898483367470","720279697515","657507942118","790570318410","671373851603","551388183855","616658456697","832824272732","714894672792","861968569418","727760709607","766142177523","862619170830","637586103814","698883133374","740744526711","926379519273","598358687603","884906702961","730177795324","644892039623","705058472150","550382355744","675076563209","595354917876","712745738555","683105787795","912738171978","626301988342","627147263711","926305281632","822273860843","682898120157","828353218044","770409757961","742855061590","842001352921","941190365257","844479922433","849520821455","688932446802","822150377419","772362660612","785499774448","818135118849","950984136695","684563539010","842249701429","717555744763","682231880696","593232961703","708570743299","902881384191","558659288784","681497540116","42534924619","691587176886","782082364301","628044230924","642279545295"]
    params = APIInfo.Params(targetId="", cookie=cookie, proxies={})
    for item_id in item_id_list[::-1]:
        params = APIInfo.Params(targetId=item_id, cookie=cookie, proxies={})
        body = asyncio.run(service.collect_url(params))
        print(body)
        #body = asyncio.run(service.item_list_url(params))
        #flag, result = service.check_item_list_body(params=params,body=body)
        #print(flag, len(result))
        time.sleep(8)

