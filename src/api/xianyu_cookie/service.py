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

class ReloginFlag(Enum):
    SUCCESS = "success"
    FAIL = "fail"
    TIMEOUT = "timeout"

class XianyuReloginService(object):

    def get_cookies(self, cookies_str, exclude_cookies=[]) -> Dict[str, str]:
        """
        过滤cookie字符串，去掉指定的字段
        """
        cookies_str = cookies_str.strip().replace(' ', '')
        cookies = {k:v for k,v in [cookie.split("=", 1) for cookie in cookies_str.split(";") if "=" in cookie]}
        for k in exclude_cookies:
            cookies.pop(k, None)
        return cookies
    
    def parse_set_cookies(self, response: Response) -> Dict[str, str]:
        """
        解析响应中的Set-Cookie头
        """
        set_cookie_list = response.headers.get_list('set-cookie')
        set_cookie_list = [i.split(";",1)[0] for i in set_cookie_list]
        set_cookie_dict = {k:v for k,v in [cookie.split("=", 1) for cookie in set_cookie_list if "=" in cookie]}
        return set_cookie_dict

    async def get_new_cookies(self, cookie_str: str, exclude_cookies = ["sgcookie"], proxies = None, timeout = 10, check_flag = lambda x: "sgcookie" in x) -> Tuple[ReloginFlag, str]:
        flag, cookies, cookie_str = await self._get_new_cookies(cookie_str, exclude_cookies, proxies, timeout, check_flag)
        unb = cookies.get("unb")
        status = 1 if flag == ReloginFlag.SUCCESS else 0
        cur_t = int(time.time())
        await source_controller.update_or_create(
            defaults={
                "value": cookie_str,
                "init_t": cur_t,
                "use_t": 0,
                "status": status
            },
            name="xianyu_cookie",
            uniq_id=unb
        )
        logger.info(f"unb {unb} relogin {flag.value}")

    async def _get_new_cookies(self, cookie_str: str, exclude_cookies = ["sgcookie"], proxies = None, timeout = 10, check_flag = lambda x: "sgcookie" in x) -> Tuple[ReloginFlag, str]:
        """执行登录状态检查请求"""
        # 请求URL
        url = 'https://passport.goofish.com/newlogin/hasLogin.do?appName=xianyu&fromSite=77'
        setting_url = "https://passport.goofish.com/ac/account/setLoginSettings.do?fromSite=77&appName=xianyu&bizEntrance=web"
        setting_data = {
            'status': '0'
        }
        
        # 请求头
        headers = {
            'accept': 'application/json, text/plain, */*',
            'accept-language': 'zh-CN,zh;q=0.9',
            'bx-v': '2.5.22',
            'content-type': 'application/x-www-form-urlencoded',
            'referer': 'https://passport.goofish.com/mini_login.htm?ttid=h5%40iframe&redirectType=iframeRedirect&returnUrl=https%3A%2F%2Fh5.m.goofish.com%2Fapp%2Fvip%2Fh5-webapp%2Flib-login-message.html%3Forigin%3Dhttps%253A%252F%252Fh5.m.goofish.com&appName=xianyu&appEntrance=web&isMobile=true',
            'user-agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 16_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.6 Mobile/15E148 Safari/604.1'
        }
        
        # 原始Cookie字符串
        
        print(exclude_cookies)
        # 过滤Cookie
        cookies = self.get_cookies(cookie_str, exclude_cookies)
        unb = cookies.get("unb")
        
        # 请求数据
        data = {
            'hid': '2219476767062' if not unb else unb,
            'ltl': 'true',
            'appName': 'xianyu',
            'appEntrance': 'web',
            '_csrf_token': '',
            'umidToken': '',
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
            'bx-ua': ''
        }
        flag = ReloginFlag.FAIL
        cookies_str = cookie_str
        try:
            print(proxies)
            async with AsyncSession() as session:
                response = await session.post(setting_url, headers=headers, data=setting_data, cookies=cookies, proxies=proxies, timeout=timeout)
                new_cookies = self.parse_set_cookies(response)
                print(new_cookies)
                cookies.update(new_cookies)
                response = await session.post(url, headers=headers, data=data, cookies=cookies, proxies=proxies, timeout=timeout)
                new_cookies = self.parse_set_cookies(response)
                print(new_cookies)
                cookies.update(new_cookies)
            cookies.update({"_rt":f"{int(time.time())}"})
            cookie_str = "; ".join([f"{k}={v}" for k,v in cookies.items()])
            flag = ReloginFlag.SUCCESS if check_flag(cookies) else ReloginFlag.FAIL
        except Exception as e:
            logger.error(f"relogin error: {traceback.format_exc()}")
            flag = ReloginFlag.TIMEOUT
        return flag, cookies, cookies_str

if __name__ == "__main__":
    service = XianyuReloginService()
    #cookie_str = 'sdkSilent=1762217869116;xlly_s=1;tfstk=guQEa4joIUX1iuH_ROLrg9n3OtTpRUyjaa9WZ_fkOpvnR2MlbtX9dgsBdbSNEOKBKM1I9GBfi2_QvUgyJULuh-ablkCpyUbZenDwp1f9Z5O3hw2xOULuhRisrHU2y9WUc2Lls5RWNDAhEBAg_IRWr2xo-cDMBQYkrLxhshABT00krpVNsddkrLXkr58MBQYkETYo607l-kdJx5O9mZrQmBKen6vZz6QwtHodtduorNSwYKDWQ40l7B5_AAvZ-rJGAgbBSw2iFFfAf9Awuzly_i5M-BW8k2Lhi1jkYarSMLINsitNXXNp_w5VzI-g7AA20NbBJGyqlKjOZa-G9-ov1gffRgWQB4vC01XwcNMslFbFLwxwog8teCbsJaIEE0-H6CJb_5rIXF5_ZlV6v0nJjCdwhWDs20KHhCJb_5o-2He6_KNnC;havana_lgc2_77=eyJoaWQiOjIyMjExNDExNjMzMDksInNnIjoiODIyODZkZWZhYWIzOWY4ZTE0ZDA1OTMwZjdlOWQ2YjAiLCJzaXRlIjo3NywidG9rZW4iOiIxUGRQZU9OUGdTOXk4X25oZk1DN3M4ZyJ9;sgcookie=E100liYPTJl9eQypR39vbJEQEyXvYJd8MDQvlydxbbI6yGyEDERFwLcMic0FTbgBcpSjlHY4BgyoMukrTQg%2FQRL0p6rjawKGlW6zJSzNKGn%2B60I%3D;_tb_token_=7dfe373bb5bbb;havana_lgc_exp=1764723466890;t=32d991de8b9d2c75c0ee2e144074e1e3;_hvn_lgc_=77;_samesite_flag_=true;cookie2=12f90198a45adf74bb820daa8ab66d0f;csg=ba5dd61d;tracknick=xy804224185746;unb=2221141163309'
    proxies = None
    #flag, cookies, cookie_str = asyncio.run(service._get_new_cookies(cookie_str, proxies=proxies)) 
    #print(flag.value)
    #print(cookies.keys())
    #print(cookies.get("sgcookie"))
    with open("xy_cookie_20251103","r") as f:
        xy_list = f.readlines()
        xy_list = [xy.strip() for xy in xy_list]
    for xy in xy_list:
        asyncio.run(service._get_new_cookies(xy, proxies=proxies))
        time.sleep(1)