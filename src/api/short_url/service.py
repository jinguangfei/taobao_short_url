import asyncio
import re
import random
import time
import json
import requests
import traceback
import httpx
from typing import Dict, Union, Any

from .config import APIInfo
from src.core.redis_script import redis_pool
from ..base.service import BaseService, APIInfo as BaseAPIInfo
from src.api.utils.taobao_req import parse_cookie_str, get_mi_id


class ShortUrlService(BaseService):
    def __init__(self):
        super().__init__()
        self.redis = redis_pool
        self.redis_key = "short_url"

    async def crawl(self, params: APIInfo.Params) -> str:
        url = APIInfo.url
        data = {
            "bizCode": "1",
            "extendInfo": f"{{\"targetId\":\"{params.targetId}\"}}",
            "targetUrl": params.targetUrl,
        }
        params = BaseAPIInfo.Params(url=url, data=data, cookie=params.cookie, proxies=params.proxies)
        body = await self._crawl(params)
        return body

    async def crawl_short_url(self, params: APIInfo.Params) -> tuple[str, Union[APIInfo.ShortInfo, None]]:
        body = await self.crawl(params)
        flag, result = self.check_body(params, body)
        return flag, result

    async def get_short_url(self, params: APIInfo.Params) -> tuple[str, Union[Dict[str, Any], None]]:
        short_url_info = self.redis.hget(self.redis_key, params.uniq_id)
        if short_url_info and not params.refresh:
            flag = "exists"
            result = json.loads(short_url_info)
        else:
            flag, result = await self.crawl_short_url(params)
            if flag in {"success"}:
                self.redis.hset(self.redis_key, params.uniq_id, result.model_dump_json())
                result = result.model_dump()
        return flag, result

    def check_body(self, params: APIInfo.Params, body: str) -> tuple[str, Union[APIInfo.ShortInfo, None]]:
        body = self._check_body(body)

        flag, result = "success", None
        recv_dict : Dict = json.loads(body) if body else {}
        short_url = recv_dict.get("data",{}).get("shortUrl","")
        long_url = recv_dict.get("data",{}).get("longUrl","")
        unb = parse_cookie_str(params.cookie).get("unb") or parse_cookie_str(params.cookie).get("munb")
        if short_url and long_url and unb:
            flag = "success"
            result = APIInfo.ShortInfo(
                short_url=short_url, 
                long_url=long_url, 
                item_id=params.targetId, 
                target_url=params.targetUrl, 
                unb=unb, 
                t=time.strftime("%Y-%m-%d %H:%M:%S"))
        elif body.find("FAIL_SYS_SESSION")>-1:
            flag = "login"
        elif body.find("RGV587_ERROR")>-1:
            flag = "deny"
        else:
            flag = "failed"
        return flag, result

if __name__ == "__main__":
    service = ShortUrlService()
    cookie = "t=6a51c62dca0a1fed922c837944eb2bee;xlly_s=1;cna=2aVvIVZMuWwCASo6I7UMcTpr;_samesite_flag_=true;cookie2=1c1d90fe4496f8d3dc0266c29afc9906;_tb_token_=3b86de3b316fe;3PcFlag=1760082650101;unb=2220983576244;lgc=tb161721913998;cancelledSubSites=empty;cookie17=UUpjNmpDK7uSQyCYmg%3D%3D;dnk=tb161721913998;tracknick=tb161721913998;_l_g_=Ug%3D%3D;sg=84a;_nk_=tb161721913998;cookie1=VAMR7PH%2BNJ%2FP6uwSaFeK5Wy5XvXZxHcqKvJ%2BySzPwbM%3D;sgcookie=E100qbOHX9oUKdDPAJHOu3tmj7XfFyYF4TBafYSXFRs0QRAlP20ZckJImTGC3sbC02VIYulC%2FnrZn33HUw0CYB7auwoIuqRMGnxmNieV1wJFLwE%3D;havana_lgc2_0=eyJoaWQiOjIyMjA5ODM1NzYyNDQsInNnIjoiZWE3NGUxNjlkMjc2NWEzZDc1NDY5YzE4N2RlMGY4MTAiLCJzaXRlIjowLCJ0b2tlbiI6IjFBX2I1QlNuRkFnVHB0UlN2NjZhcFBBIn0;_hvn_lgc_=0;cookie3_bak=1c1d90fe4496f8d3dc0266c29afc9906;cookie3_bak_exp=1760341863390;sn=;uc3=lg2=Vq8l%2BKCLz3%2F65A%3D%3D&vt3=F8dD2k0%2FEBqMJeaczUk%3D&nk2=F5REODKXK01oxNqCGoI%3D&id2=UUpjNmpDK7uSQyCYmg%3D%3D;csg=d16f054f;env_bak=FM%2BgndCFyBqv0r%2Ffy5GhfapgbppXF95%2BathN4UJtkZz7;skt=23506d729896c2b1;existShop=MTc2MDA4MjY2Mw%3D%3D;uc4=id4=0%40U2gp9rlpS9zkO%2B7Fa1ztLT8XFDnIPJUY&nk4=0%40FY4PamxpPd9soxfRwCyiFZ0UTH0aYncnHw%3D%3D;_cc_=VT5L2FSpdA%3D%3D;havana_lgc_exp=1791186681952;_m_h5_tk=c6f6dc0f73c27159123c624462b9a123_1760093156109;_m_h5_tk_enc=dbb741a5a56befbd32263045d986d979;thw=cn;isg=BAIC_O1T3jVTYMLpx6q1DrVeUwhk0wbtx5lZd0wbTHUgn6AZNmHx_HFcS5vjz36F;sdkSilent=1760111481952;havana_sdkSilent=1760111481952;uc1=cookie14=UoYY4%2Fvpox9c9A%3D%3D&existShop=false&pas=0&cookie15=URm48syIIVrSKA%3D%3D&cookie21=UtASsssmfufd&cookie16=V32FPkk%2FxXMk5UvIbNtImtMfJQ%3D%3D;mtop_partitioned_detect=1;aui=2220983576244;sca=dacdeab7;tfstk=g29mG32jGI5jgKebicXjM8DG7RGJct61MFeOWOQZaa75MmOvXQvGrHofkfGXSQYwPsQ2IhwGbh8scNnjwntfCOuKJFDpcn_BnmeIyOow4OIMVzwaIntfCugKJvHpcl4jcNKVbNolUGjG0OS4304PxayVb-Saz0j1zOWNQFR5ILbP7OWw73olfa7NQOkLQo7eQCJr7WS23HV_1Ljciw2FrR2iXifc8n7lVg9P5sbe0a2Zu2D9oNbWL4hkVQO2kgTiK4X6PC8NjUzrWstwZUjDk241WKtvIgtmgqxlUZxNsE00GZRvr6sPTvqlcKpdOw1obR1OHpCeTdiL63dkzKApn4yw7tQcHKW_jJY1eZ1HH9kQuNdJxdjMCVMk-H9Wrg8EIqSzJ7PESGy1JYx_151VVgbdPCo7btIscHnoqWO1ggshJ0mu151VVgbKq0VOvsS5qjf.."
    mi_id = asyncio.run(get_mi_id())
    params = APIInfo.Params(targetId="834550783063", targetUrlType="TAOBAO", cookie=cookie, proxies={}, mi_id=mi_id)
    body = asyncio.run(service.crawl(params))
    #body = '{"api":"mtop.taobao.sharepassword.generateshorturlnew","data":{"shortUrl":"https://e.tb.cn/h.SXjcgDZgiZ8HovB","longUrl":"https://main.m.taobao.com/app/ltao-fe/we-detail/home.html?id=834550783063&un=1dc7d07188ad17b09a94a88b634b6e7e&share_crt_v=1&un_site=18"},"ret":["SUCCESS::调用成功"],"traceId":"213e0a0d17581872240356042e11b2","v":"1.0"}'
    #result = service.check_body(params, body)
    #print(result)