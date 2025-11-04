import asyncio
import traceback
from curl_cffi.requests import AsyncSession
from curl_cffi.requests.models import Response
from typing import Dict, Tuple
from enum import Enum
import time
from src.core.redis_script import redis_pool
from src.loger import logger
from .config import APIInfo
from src.api.source.service import source_controller
from src.api.utils.func import parse_cookie_str, parse_set_cookies
from pydantic import BaseModel

class Account(BaseModel):
    login_id : str
    password : str
    umidToken : str
    bx_umidtoken: str

class ReloginFlag(Enum):
    SUCCESS = "success"
    FAIL = "fail"
    TIMEOUT = "timeout"

class DamaiReloginService(object):
    def __init__(self, name : str = "damai_cookie"):
        self.name = name

    async def get_new_cookies(self, account: Account, cookie_str: str, exclude_cookies = ["sgcookie"], proxies = None, timeout = 10, check_flag = lambda x: "sgcookie" in x) -> Tuple[ReloginFlag, str]:
        flag, cookies, cookie_str = await self._get_new_cookies(account, cookie_str, exclude_cookies, proxies, timeout, check_flag)
        unb = cookies.get("unb") or cookies.get("munb")
        status = 1 if flag == ReloginFlag.SUCCESS else 0
        cur_t = int(time.time())
        await source_controller.update_or_create(
            defaults={
                "value": cookie_str,
                "init_t": cur_t,
                "use_t": 0,
                "status": status
            },
            name=self.name,
            uniq_id=unb
        )
        logger.info(f"unb {unb} relogin {flag.value}")

    async def _get_new_cookies(self, account: Account,cookie_str: str, exclude_cookies = ["sgcookie"], proxies = None, timeout = 10, check_flag = lambda x: "sgcookie" in x) -> Tuple[ReloginFlag, Dict[str, str], str]:
        """执行登录状态检查请求"""
        # 请求URL
        url = 'https://ipassport.damai.cn/newlogin/login.do?appName=damai&fromSite=18'
        # 请求头
        headers = {
            'accept': 'application/json, text/plain, */*',
            'accept-language': 'zh-CN,zh;q=0.9',
            'bx-v': '2.5.22',
            'content-type': 'application/x-www-form-urlencoded',
            'referer': 'https://www.damai.cn/',
            'user-agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 16_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.6 Mobile/15E148 Safari/604.1'
        }
        
        # 原始Cookie字符串
        
        # 过滤Cookie
        cookies = parse_cookie_str(cookie_str, exclude_cookies)
        unb = cookies.get("unb") or cookies.get("munb")
        
        # 请求数据
        data = {
            'loginId': account.login_id,
            'password2': account.password,
            'keepLogin': 'false',
            'ltl': 'true',
            'appName': 'damai',
            'appEntrance': 'web',
            '_csrf_token': '',
            'umidToken': account.umidToken,
            'hsiz': '',
            'bizParams': 'taobaoBizLoginFrom%3Dgoofish%26renderRefer%3Dhttps%253A%252F%252Fh5.m.goofish.com%252Fapp%252FidleFish-F2e%252Ffish-mini-pha%252Fsearch-result.html%253Fkeyword%253D%2525E7%252583%2525AD%2525E6%2525B0%2525B4%2525E8%2525A2%25258B%2526spm%253Da2170.12485125.0.0',
            'mainPage': 'false',
            'redirectType': 'iframeRedirect',
            'isMobile': 'true',
            'lang': 'zh_CN',
            'returnUrl': 'https://h5.m.goofish.com/app/vip/h5-webapp/lib-login-message.html?origin=https%3A%2F%2Fh5.m.goofish.com',
            'fromSite': '77',
            'isIframe': 'true',
            'documentReferer': 'https://h5.m.goofish.com/app/idleFish-F2e/fish-mini-pha/search-result.html?keyword=%E7%83%AD%E6%B0%B4%E8%A2%8B&spm=a2170.12485125.0.0',
            'defaultView': 'hasLogin',
            'umidTag': 'SERVER',
            'deviceId': '',
            'pageTraceId': '',
            'bx-umidtoken': account.bx_umidtoken,
            'bx-ua': ''
        }
        flag = ReloginFlag.FAIL
        cookies_str = cookie_str
        try:
            async with AsyncSession() as session:
                response = await session.post(url, headers=headers, data=data, cookies=cookies, proxies=proxies, timeout=timeout)
                new_cookies = parse_set_cookies(response)
                cookies.update(new_cookies)
            cookies.update({"_rt":f"{int(time.time())}"})
            cookie_str = "; ".join([f"{k}={v}" for k,v in cookies.items()])
            flag = ReloginFlag.SUCCESS if check_flag(cookies) else ReloginFlag.FAIL
        except Exception as e:
            logger.error(f"relogin error: {traceback.format_exc()}")
            flag = ReloginFlag.TIMEOUT
        return flag, cookies, cookies_str

if __name__ == "__main__":
    service = DamaiReloginService()
    with open("src/api/damai_cookie/damai_acount","r") as f:
        account_list = f.readlines()
        account_list = [i.strip().split(" ") for i in account_list]
        account_list = [Account(login_id=i[0], password=i[1], umidToken=i[2], bx_umidtoken=i[3]) for i in account_list]
    
    cookie_str = 'x5sec=7b22733b32223a2235656665636464306531393566363866222c22617365727665723b33223a22307c434a7a6570736747454c5755676272342f2f2f2f2f774561447a49794d5463314e7a6b304d6a67314e5441374d53494b59324677633278705a4756324d696941424444576a626e6142673d3d227d'
    proxies = None
    flag, cookies, cookie_str = asyncio.run(service._get_new_cookies(account_list[0], cookie_str, proxies=proxies)) 
    print(flag.value)
    print(cookies.keys())
    print(cookies.get("sgcookie"))