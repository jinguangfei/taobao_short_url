import asyncio
from hmac import new
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

class ReloginFlag(Enum):
    SUCCESS = "success"
    FAIL = "fail"
    TIMEOUT = "timeout"

class XianyuReloginService(object):

    def __init__(self, name : str = "xianyu_cookie"):
        self.name = name

    async def get_new_cookies(self, cookie_str: str, exclude_cookies = ["sgcookie"], proxies = None, timeout = 10, check_flag = lambda x: "sgcookie" in x) -> Tuple[ReloginFlag, Dict[str, str], str]:
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
        return flag, cookies, cookie_str

    async def _get_new_cookies(self, cookie_str: str, exclude_cookies = ["sgcookie"], proxies = None, timeout = 10, check_flag = lambda x: "sgcookie" in x) -> Tuple[ReloginFlag, Dict[str, str], str]:
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
        
        # 过滤Cookie
        cookies = parse_cookie_str(cookie_str, exclude_cookies)
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
                new_cookies = parse_set_cookies(response)
                print(new_cookies)
                cookies.update(new_cookies)
                response = await session.post(url, headers=headers, data=data, cookies=cookies, proxies=proxies, timeout=timeout)
                print(response.text)
                new_cookies = parse_set_cookies(response)
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
    proxies = None
    #with open("xy_cookie_20251103","r") as f:
    #    xy_list = f.readlines()
    #    xy_list = [xy.strip() for xy in xy_list]
    #for xy in xy_list:
    #    asyncio.run(service._get_new_cookies(xy, proxies=proxies))
    #    time.sleep(1)
    xy = "_m_h5_tk_enc=679c67a1e76f8bfa3dd54beae1c3235c;sdkSilent=1767927692023;xlly_s=1;tfstk=g5unBN2t-R6jVpBwoTzBYHZcnDtTRya7bYQ8ezeybRy1p9QKaTDoQxhdJ4hzEYDTCXQJOXCIfxhVJ2KQya4QPzJvHELvAXa7z6Q1d_eI_fNy6WSMAQ6QPzJvBGQzAE4SKptlFzlws7FRYgkzaPWaCSFUzJrPQGP4Q8zrUJraQ7V5LaPFzCcaC7zzUYzysly_azyrUzl6v6y0DluweUpdUxJ9BVV3x8b8IabywWq33XyM3KuMPk2qTRbyKl3wKRPm7L6LFVcZ8SHwWw4o_7D08cvN-YcEcYNqLFXUtDlmMl0W3aVsbvZTtcAPbJl4LvqnmOR3F2Hnrkg2HNwEjVguJcphk8ZrX2ZjJd73umGLJ0kwaayob7SP_GSqdgQ7_Q3NVgZU152ABaSW0HGkDYdMsis7Y5NEaCAGVUqU152vsCj2gkP_Tb5..;havana_lgc2_77=eyJoaWQiOjIyMjExMjI3ODU4NzMsInNnIjoiNDI5NDgzYjM1N2Q0OGZkZDE0MjAwZmQ0Njk4MWE5ZmMiLCJzaXRlIjo3NywidG9rZW4iOiIxX3dvZ1ZBUnl4NGlKR1RRaTBWSDRwUSJ9;sgcookie=E100uefea1k1WBhOPTCJUEhAYt%2BYVmzjE3vid6Cw1vuHGbbYWXnBmJm8DVk6TTZy3BF8bO1RYJl5BOnLmq26tpOc%2F5gi%2FfR3RTCEvb4s3kfqofI%3D;_tb_token_=59eea8783e765;havana_lgc_exp=1770433289900;t=6c96c60047713d630c0696bd66f90ca2;_hvn_lgc_=77;_m_h5_tk=15938a1dd455fd734fcadae6a4b5b46d_1767851422859;_samesite_flag_=true;cookie2=1e2c832d9bede962559bd95efeed8535;csg=d630b18f;tracknick=xy171704223073;unb=2221122785873"
    flag,cookies,cookie_str = asyncio.run(service._get_new_cookies(xy, proxies=proxies))
    print(flag.value)
    print(cookies)
    print(cookie_str)