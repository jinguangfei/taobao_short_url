import re
import time
import json
import requests
import traceback
from typing import Dict, Union

from .config import APIInfo
from ..utils import parse_url, md5_data


class ShortUrlService(object):
    def __init__(self):
        self.api_info = APIInfo

    def parse_cookie_str(self, cookie_str : str) -> dict:
        cookie_dict = {i.split("=")[0]:i.split("=",1)[1] for i in cookie_str.replace("; ",";").split(";") if len(i.split("="))>1}
        return cookie_dict

    def build_url(self, params: APIInfo.Params):
        headers = self.api_info.headers
        proxies = params.proxies
        url , query_params = parse_url(self.api_info.url)
        cookies = self.parse_cookie_str(params.cookie)

        data = {
            "bizCode":"1",
            "extendInfo":f"{{\"targetId\":\"{params.targetId}\"}}",
            "targetUrl":params.targetUrl,
        }
        data_str = json.dumps(data).replace(" ", "")

        tk_g = re.search(r"_m_h5_tk=(.*?)_",params.cookie)
        tk = tk_g.group(1) if tk_g else ""

        t, sign, data_str = md5_data(tk, data_str, app_key="21783927")
        query_params["data"] = data_str
        query_params["sign"] = sign
        query_params["t"] = t

        return url, query_params, headers, cookies, proxies

    def crawl(self, params: APIInfo.Params) -> str:
        url, query_params, headers, cookies, proxies = self.build_url(params)
        try:
            res = requests.get(url, headers=headers, params=query_params, timeout=10, cookies=cookies, proxies=proxies, timeout=20)
            return res.text
        except Exception as e:
            print(traceback.format_exc())
            return ""

    def _check_body(self, body: str) -> str:
        if body.find("mtopjsonp")>-1:
            body = body[body.find("(")+1:-1].replace("({","{",1)
        return body

    def check_body(self, params: APIInfo.Params, body: str) -> tuple[str, Union[APIInfo.ShortInfo, None]]:
        body = self._check_body(body)

        flag, result = "success", None
        recv_dict : Dict = json.loads(body)
        short_url = recv_dict.get("data",{}).get("shortUrl","")
        long_url = recv_dict.get("data",{}).get("longUrl","")
        unb = self.parse_cookie_str(params.cookie).get("unb")
        if short_url and long_url and unb:
            flag = "success"
            result = APIInfo.ShortInfo(
                short_url=short_url, 
                long_url=long_url, 
                item_id=params.targetId, 
                target_url=params.targetUrl, 
                unb=unb, 
                t=time.strftime("%Y-%m-%d %H:%M:%S"))
        else:
            flag = "failed"
        return flag, result

if __name__ == "__main__":
    service = ShortUrlService()
    cookie = "sn=;t=4a2f90bf201915adc4053ed881157199;existShop=MTc1ODE3NTQ2NA%3D%3D;cookie1=UofgJ%2BzVfUtotmhxEmZk8ClhRqJz5gpKjVJkhMrMPcI%3D;csg=46a31360;wk_cookie2=11c8567a39adfdbfd489297a45edd842;cookie2=1338b9f8d1ca478f7c24ab13b90aaec4;xlly_s=1;sca=7b12784a;skt=c24230369c9b6560;unb=2220079476714;_tb_token_=7538333e537f7;sgcookie=E100UUDho8RqcQR2%2BLMYlRm5D3NRRpHRhJBRlTMXiruInCPK0ptizgn%2BOkx%2BSzAm7%2FoE7Cs639PwMSvT9uRvw%2BEQZhBrzKl%2FHj5MO4cRFSXIQmQ%3D;aui=2220079476714;_samesite_flag_=true;cna=eA6sHZIYAXICAWUn3Y7K1J8U;tfstk=gGutL124sBC9iuWN6xxHopDFbCA3MHcZ9Al5o-2GcvHKIbigjjw0kxHxHRqXQP0xpAcSjlcjoSgY72mGoRvakjMukLvkrUcZ_PUXELXG2bdulST0hHq66g1k6Lvkrex1Orp9ExDeyfZQgJN_GGaX9WNa1rNbcZOLdSFPcOMblBdLGSf1hZwjOkNzZrwjhlOKOJPbl5MblBhQLSGtChed1WQxfumRoLQg6Z_jJ5EBxfeB5buL6PwS1XQflgNTX8G_pLn719rxBl3HWTPtAbHg6x8P7PZxf0askLLTRbonCWHXeieI2VuYqVpR4Rga3YUsvp_TlPgtquzv21PnWXgzDVJORRHEO04ZPp7xFXco7kuve9wqj7zQ6DdfARZf4AuoyFhlE8FcfBdd0ir_TZ2MEyYYqTDQ98AT6iS4cWPLEBp50ir_TWek6MjV0k5G.;wk_unb=UUpjNmPAHqUkTsEOfQ%3D%3D;_cc_=WqG3DMC9EA%3D%3D;thw=cn;_m_h5_tk_enc=864c90cdb6d1cbb44209ba6ed0229b48;isg=BHR0ozxpoGwqnDr4xcgGqNjwRTTmTZg3JX030w7VIP-CeRTDNlwzxzwp-7GhmtCP;3PcFlag=1758175459244;_hvn_lgc_=0;_l_g_=Ug%3D%3D;_m_h5_tk=e8e6f7a6b7bd7d0852cd3594ce69e02e_1758183376952;_nk_=tb545027396494;cancelledSubSites=empty;cookie17=UUpjNmPAHqUkTsEOfQ%3D%3D;dnk=tb545027396494;havana_lgc2_0=eyJoaWQiOjIyMjAwNzk0NzY3MTQsInNnIjoiMzIxNGYyNDM4OGRjNzU0NWE1MGIwZDQzNjkyZGZhMzgiLCJzaXRlIjowLCJ0b2tlbiI6IjFJb3IyRV9TWWxKUGt2b1NOWVREVUhnIn0;havana_lgc_exp=1789279464797;havana_sdkSilent=1758204264797;lgc=tb545027396494;sdkSilent=1758204264797;sg=44c;tracknick=tb545027396494;uc1=cookie14=UoYbw14ZT408BQ%3D%3D&cookie16=Vq8l%2BKCLySLZMFWHxqs8fwqnEw%3D%3D&existShop=false&cookie15=WqG3DMC9VAQiUQ%3D%3D&pas=0&cookie21=UIHiLt3xTIkz;uc3=lg2=V32FPkk%2Fw0dUvg%3D%3D&vt3=F8dD2k%2FrcmCaDrpMPvE%3D&id2=UUpjNmPAHqUkTsEOfQ%3D%3D&nk2=F5RARoQHaSbFSSIayQk%3D;uc4=id4=0%40U2gp9rB6M%2F6NN56nOCd3memW6FxEJBpS&nk4=0%40FY4L6okdjAd%2Fi1p2W2eRsBdpJtON4FIP5A%3D%3D"
    params = APIInfo.Params(targetId="834550783063", targetUrlType="LT_TAOBAO", cookie=cookie, proxies={})
    body = service.crawl(params)
    #body = '{"api":"mtop.taobao.sharepassword.generateshorturlnew","data":{"shortUrl":"https://e.tb.cn/h.S25GasXAiLwQVGp","longUrl":"https://main.m.taobao.com/app/ltao-fe/we-detail/home.html?id=834550783063&un=d7dd62e400a10e264858dbc0573c2db7&share_crt_v=1&un_site=0"},"ret":["SUCCESS::调用成功"],"traceId":"213e097717581789403278048e119b","v":"1.0"}'
    result = service.check_body(params, body)
    print(result)