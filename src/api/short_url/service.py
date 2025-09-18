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


class ShortUrlService(object):
    def __init__(self):
        self.api_info = APIInfo
        self.taobao_tk_service = TaobaoTkService()

    def parse_cookie_str(self, cookie_str : str) -> dict:
        cookie_dict = {i.split("=")[0]:i.split("=",1)[1] for i in cookie_str.replace("; ",";").split(";") if len(i.split("="))>1}
        return cookie_dict

    async def build_url(self, params: APIInfo.Params):
        headers = self.api_info.headers
        proxies = params.proxies
        url , query_params = parse_url(self.api_info.url)
        tk_cookie = await self.taobao_tk_service.get_taobao_tk()
        cookies = self.parse_cookie_str(params.cookie+f";{tk_cookie}")

        data = {
            "bizCode":"1",
            "extendInfo":f"{{\"targetId\":\"{params.targetId}\"}}",
            "targetUrl":params.targetUrl,
        }
        data_str = json.dumps(data).replace(" ", "")
        print(cookies.get("_m_h5_tk",""))

        tk_g = re.search(r"_m_h5_tk=(.*?)_",tk_cookie)
        tk = tk_g.group(1) if tk_g else ""

        t, sign, data_str = md5_data(tk, data_str, app_key="21783927")
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

    def check_body(self, params: APIInfo.Params, body: str) -> tuple[str, Union[APIInfo.ShortInfo, None]]:
        body = self._check_body(body)

        flag, result = "success", None
        recv_dict : Dict = json.loads(body)
        short_url = recv_dict.get("data",{}).get("shortUrl","")
        long_url = recv_dict.get("data",{}).get("longUrl","")
        unb = self.parse_cookie_str(params.cookie).get("unb") or self.parse_cookie_str(params.cookie).get("munb")
        print(short_url, long_url, unb)
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
    cookie = "damai_cn_user=0y7YhxL4oOaoCx2IYyA4kUGAAStSdau1qAwSAAPQG4IOvLFhUyR0QLNM6UDtEV80Gxb2%2BRjuqig%3D;user_id=482302508;csg=134c9ba9;damai.cn_nickName=%E9%BA%A6%E5%AD%907o4GQ;isg=BHx8i2j4OMSfqQE9os-uRpuRTRwudSCfXRUvy1b9gWdKIRyrfoOPL8-aBUlZXVj3;tfstk=gQnKjxNzKdBLkp5FpbYMqd4Q_FpMoFDeXXkfq7VhPfhttY9FxWqowzM4s0vEKe--WbGgOy0nE3hi_flnKYD5e8GgAzu3ZWV82YlvIIxDmvkU4kADinYH5oAg0J6CA_q6f8r8d8MKnvHU4uOmEVIHsvlFYPRYVu9Tf8eAAuN7Ode_e5sQFMw51dez1uw7Nut_18wuFgsINA9TU5N7VuG7fdez17Z7VfQDJ5BQBg3Qy72DpTedVgiTpPTiK51TrcyLWSMIBgsWhJULGvN9gMEvGzhLJcxdgJ3sHX2KanSUAz3IlkiJMHEs3VcQBbOAy5gxY0UmvIQ4ODPrMkg91ME7AD30uuLALRmKCmz-YBI_9fksokoX_ghjIxmU70dA17u33lwKWL__Ozsynmmvvxf0M8bpBdQPzywNqWA0jHPP_u2Tipedzaz7QRFDBI_PzywaBSvdSa7z79f..;cookie2=12406d282b4e488263dac6920574fb00;_hvn_login=18;_samesite_flag_=true;_tb_token_=e5eb94635333a;damai.cn_user=0y7YhxL4oOaoCx2IYyA4kUGAAStSdau1qAwSAAPQG4IOvLFhUyR0QLNM6UDtEV80Gxb2+Rjuqig=;damai.cn_user_new=0y7YhxL4oOaoCx2IYyA4kUGAAStSdau1qAwSAAPQG4IOvLFhUyR0QLNM6UDtEV80Gxb2%2BRjuqig%3D;h5token=76db359c6fb845b0b7daf1a9f6b549d7_1_1;loginkey=76db359c6fb845b0b7daf1a9f6b549d7_1_1;munb=2217579428550;sgcookie=E100KLSy5UHTRBbytlfyCO%2FEl0%2FLjWxJg0ryOM7WhU0Gwgl51M6%2BwYRF997ZAFPVeW6fkzV%2Bz69rLGYgvQ%2BHaZ3wRDfjX8JmsF3Tb1a1ND%2B20DQ%3D;t=7e619c559d5c20ee63d3993b16e89ee4;xlly_s=1"
    params = APIInfo.Params(targetId="834550783063", targetUrlType="LT_TAOBAO", cookie=cookie, proxies={})
    #body = asyncio.run(service.crawl(params))
    #print(body)
    body = '{"api":"mtop.taobao.sharepassword.generateshorturlnew","data":{"shortUrl":"https://e.tb.cn/h.SXjcgDZgiZ8HovB","longUrl":"https://main.m.taobao.com/app/ltao-fe/we-detail/home.html?id=834550783063&un=1dc7d07188ad17b09a94a88b634b6e7e&share_crt_v=1&un_site=18"},"ret":["SUCCESS::调用成功"],"traceId":"213e0a0d17581872240356042e11b2","v":"1.0"}'
    result = service.check_body(params, body)
    print(result)