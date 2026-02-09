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

class ReloginFlag(Enum):
    SUCCESS = "success"
    FAIL = "fail"
    TIMEOUT = "timeout"

class TaobaoReloginService(object):
    def __init__(self, name : str = "taobao_cookie"):
        self.name = name

    async def get_new_cookies(self, cookie_str: str, exclude_cookies = ["sgcookie"], proxies = None, timeout = 10, check_flag = lambda x: "sgcookie" in x) -> Tuple[ReloginFlag, Dict[str, str], str]:

        flag, cookies, cookie_str = await self._get_new_cookies(cookie_str, exclude_cookies, proxies, timeout, check_flag)
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
        return flag, cookies, cookie_str

    async def _get_new_cookies(self, cookie_str: str, exclude_cookies = ["sgcookie"], proxies = None, timeout = 10, check_flag = lambda x: "sgcookie" in x) -> Tuple[ReloginFlag, Dict[str, str], str]:
        """执行登录状态检查请求"""
        # 请求URL
        url = 'https://login.taobao.com/newlogin/hasLogin.do?appName=taobao&fromSite=77'
        #url = 'https://ipassport.damai.cn/newlogin/hasLogin.do?appName=damai&fromSite=77'
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
        unb = cookies.get("unb") or cookies.get("munb")
        
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
            async with AsyncSession() as session:
                response = await session.post(url, headers=headers, data=data, cookies=cookies, proxies=proxies, timeout=timeout)
                new_cookies = parse_set_cookies(response)
                cookies.update(new_cookies)
            cookies.update({"_rt":f"{int(time.time())}"})
            cookie_str = "; ".join([f"{k}={v}" for k,v in cookies.items()])
            print(cookie_str)
            flag = ReloginFlag.SUCCESS if check_flag(cookies) else ReloginFlag.FAIL
        except Exception as e:
            logger.error(f"relogin error: {traceback.format_exc()}")
            flag = ReloginFlag.TIMEOUT
        return flag, cookies, cookies_str

if __name__ == "__main__":
    service = TaobaoReloginService()
    cookie_str = 'sn=;t=1de517b10f41f87e255d2ea1490ef8fb;existShop=MTc2NjA2Nzk2OQ%3D%3D;cookie1=Vyh9yAFHq2wW3NJSikvgn0VL7t3Ezsy3EMJtx91wrKI%3D;csg=ee58a455;cnaui=2219207382449;wk_cookie2=1f7538fed5ad4a2a41130f5a91acc71f;cookie2=1bec3c4472ad68e6c29342ccc89dda32;xlly_s=1;sca=8dd7feaa;skt=3dfd2952e7667131;unb=2219207382449;_tb_token_=56865ee73e397;sgcookie=E100YCe%2Bkah7aNnBUCTXL4HXwlPVF471xF9WfsrMFCopvkJXiTIPAeuebYjYRhuWDKYIu4BPXPZrLRJuELYw1ihL6hBRJ4zJz9WcbLIsocjIzQs%3D;miid=7366606780128398448;aui=2219207382449;_samesite_flag_=true;tfstk=gjHS32XuQ2H4SCxJJa-VlzU9wQwB7nJZvMZKjDBPv8eRJ2iIkvPL8Q0QO2u09Yyr4q9IjVNzykFLMiEgxuULy_nYMrgRL7kIx9ZKv2xu83Aqq023pF8ZOdooqSu8zu84pHnYLkgBUBt-q02hmF8wQdokdAv8y2ELJnwYAlC8pTeLDnZUfweLyWQAMlUYJJ3KJmKbxrULpJ3KDnZ3kyeK1hWbAt4qVhSnphL3tPn8l9BCjuN8Wd4fp9HbVNztVCXdpxZ7NxgfRYMQpbnrl5lW5Twn2f03X4QJPoMSfvGtkKW7dmhtd-Hvkiz-smMQUYKee-HSPYFjJMtYkvZsA5l2v1aq9mDbGYONxoDrvYVaBdb88josdkMH-Kgs24GT6YQ5406a5tzhOiNGdoawcn1hty63yVjWqt9Uwoq77ntf_3N8mowWcn1ht7E00AtXc1-5.;wk_unb=UUpgT71fE0l%2FZyt0CQ%3D%3D;_cc_=VT5L2FSpdA%3D%3D;thw=cn;_m_h5_tk_enc=2172bab8fb2fc20c4923e0ca8ec537c9;x5sec=7b2274223a313736363039383839342c22733b32223a2230376432303336343633643563343262222c22617365727665723b33223a22307c434d79506b736f47454f574367706e362f2f2f2f2f774561447a49794d546b794d44637a4f4449304e446b374d544351344e53442b502f2f2f2f3842227d;isg=BJ6eBrcPe42sjK5gEzDNT0Xr7zLgX2LZzd8D_EgnBOHcaz5FsO6J6cFIZ3fn01rx;3PcFlag=1766067964473;_hvn_lgc_=0;_l_g_=Ug%3D%3D;_m_h5_tk=1d31cc1c755129144355c995061940fc_1766106056313;_nk_=tb814382489294;bxuab=0;cancelledSubSites=empty;cookie17=UUpgT71fE0l%2FZyt0CQ%3D%3D;dnk=tb814382489294;havana_lgc2_0=eyJoaWQiOjIyMTkyMDczODI0NDksInNnIjoiZjQ5MzViM2M3ODIzNzM5OWI5NGEzZTU1NzNmZTdmYTQiLCJzaXRlIjowLCJ0b2tlbiI6IjFyLUtzWW9Eak9UUzAyc3RQaEtYRjR3In0;havana_lgc_exp=1797202853894;havana_sdkSilent=1766127653894;lgc=tb814382489294;sdkSilent=1766127653894;sg=491;tracknick=tb814382489294;uc1=cookie15=URm48syIIVrSKA%3D%3D&existShop=false&pas=0&cookie14=UoYY5RBnAidrRg%3D%3D&cookie21=V32FPkk%2Fhw%3D%3D&cookie16=WqG3DMC9UpAPBHGz5QBErFxlCA%3D%3D;uc3=vt3=F8dD2keqlJqAFZ%2FoITc%3D&lg2=UtASsssmOIJ0bQ%3D%3D&nk2=F5RNZLRUvA5xe6%2BhO9Y%3D&id2=UUpgT71fE0l%2FZyt0CQ%3D%3D;uc4=nk4=0%40FY4Gs4PG%2Bdf9wl6t8ta0x10TlmuMHIQvWA%3D%3D&id4=0%40U2gqwAJDDOA8b7pqtTxT5rn%2B1JAAL8c5'

    #cookie_str = cookie_str + ";last_cc=EDD840ABEE517462139AC69D0B129DDE;last_u_damai_damai=eyJoaWQiOjIyMTc1NzkxODEwMjksImxvZ2luSWQiOiIxODg5Mzg0ODQ0NSIsInNnIjoiMmZhZHNiOTliMWZhY2Y3ZTYzNzE1NDQ5M2Q5MWNiZWMzNGQyZiJ9;_hvn_login=18;havana_tgc=eyJjcmVhdGVUaW1lIjoxNzYyMTMzNzYyMjE4LCJsYW5nIjoiemhfQ04iLCJwYXRpYWxUZ2MiOnsiYWNjSW5mb3MiOnsiMTgiOnsiYWNjZXNzVHlwZSI6MSwibWVtYmVySWQiOjIyMTc1NzkxODEwMjksInRndElkIjoiMUR6eV9DajNMQ3NCVE50WnB3RkNsUncifX19fQ;x5sec=7b22733b32223a2265326135373032333738386137616366222c22617365727665723b33223a22307c434932506f4d6747454a6246342b3445476738794d6a45334e5463354d5467784d4449354f7a4569436d4e6863484e736157526c646a496f67415177316f32353267593d227d"
    proxies = None
    flag, cookies, cookie_str = asyncio.run(service._get_new_cookies(cookie_str, proxies=proxies)) 
    print(flag.value)
    print(cookies.keys())
    print(cookies.get("sgcookie"))