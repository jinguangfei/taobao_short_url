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
                cookies.update(new_cookies)
                response = await session.post(url, headers=headers, data=data, cookies=cookies, proxies=proxies, timeout=timeout)
                new_cookies = self.parse_set_cookies(response)
                cookies.update(new_cookies)
            cookies.update({"_rt":f"{int(time.time())}"})
            cookie_str = "; ".join([f"{k}={v}" for k,v in cookies.items()])
            flag = ReloginFlag.SUCCESS if check_flag(cookies) else ReloginFlag.FAIL

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
        except Exception as e:
            logger.error(f"relogin error: {traceback.format_exc()}")
            flag = ReloginFlag.TIMEOUT
        return flag, cookies, cookies_str

if __name__ == "__main__":
    service = XianyuReloginService()
    cookie_str = '_m_h5_tk_enc=12313281cfd1a699902fe64afee2dc83;sdkSilent=1753998364341;xlly_s=1;tfstk=gSGoZbqxZoss4lKYHjNWFx250W9xN7NQ3DCLvWEe3orf2gC-8Mmn0c3RwX3UxDmYc4CpP4QShc3Nwbp796V7OW-9XCd9F4NQTP0IqFrSuqaekzWDFes7OW-9DtCUFCVI45XDK4u2oyUdayoUzsW4cy4PaDrz3izg5WPEYuPVuzUOz6rz8o80RorUTWoEuE4L0klC6argB-l2xfolGqVe0nF_Eluzm10jMz57fCZcT6l0rqqZzO1FTj4uEX19r65zTYu-mRHkj_VIzAiQ70SyqrcoSXDZ0ICutqkZtSl20ZErCqc3wb8paSloqbymYwY40X4i-RHv8OqxLqG0nbvORrG-8bwT_Cszvx3itycBAImiz0DaQbSl4_XVQrpROr8Kg96QUra0XFeCvQpMsrdBoEX1d8zbz28Do9_8Ura0XEYcQqezlzuF.;havana_lgc2_77=eyJoaWQiOjE2NTA2MDcwMjYsInNnIjoiN2QyNzViODVhNzEzMWU3NWUxMjhlNmY3OTU2YjY5OTIiLCJzaXRlIjo3NywidG9rZW4iOiIxSUZHNjA1NWNCVU96dE15SFhuVERfQSJ9;sgcookie=E100Od16OoUyPEl3sF3zbJcjb5ApCYzbkPTD0k4kOHEGCJDlHkniDvwHM8CT1nDR0JssKEmrWLOImBgWPddEmBfM%2FYjhkDL%2Bggr7B7We7uWdg1M%3D;_tb_token_=6ff30b97fb36;havana_lgc_exp=1756100957104;t=398788f7536d3ca79ce42f99387fb883;_hvn_lgc_=77;_m_h5_tk=e0154115d933c7089cf10b7e948a4c42_1754050167330;_samesite_flag_=true;cookie2=11cf24b1f66b844786bedddd951e798c;csg=ab6ccdec;tracknick=%E9%87%91%E5%85%89%E9%A3%9E%E8%B7%83;unb=1650607026'
    cookie_str = '_m_h5_tk_enc=03930128e1d613567a334c6cc0671367;sdkSilent=1761368454864;xlly_s=1;tfstk=gRvxZhbHM0EvqOz4DFcosi4mR7noZbx4mE-QINb01ULJAHzc1KXDW5LDbFfsutv9ytJkiRbmuOK6-O3n-vDH0nWVC20Hr8AZNOssINGlGaN-kkgn-vDoGu6tk2YgrxePFG75cG__G0E5YGW1ci_j2asOY5aX5Oi-2MjgcR615_t5Ya_1COT6V0INPi61CFtS2G8z4jQSrwy9gIFs2cnoRP4MeiCAWRb8B7oGDsQBca3IRLpNMwtfyRgjW10CPMpS7rbwe39fbUMuHOK5XeBXw4wvWnOe7MTjersvGHKhwduQBgRWu_jvwcN5lH_VhapZbR7Xih9G6KgQjZ92oLCeQr3lSBxkh_LIr8LN6IOChd3KFg-vKpKXVybdjSi-25PNGgWQiqaASDrUigQnDmFa__LA2wm-R5N_8-SR-0b7_55Jq;havana_lgc2_77=eyJoaWQiOjE2NTA2MDcwMjYsInNnIjoiMDU0NzMyMzc1ZTVhYWU0NzZmNzc1MWZiMTdjMTI2ZTciLCJzaXRlIjo3NywidG9rZW4iOiIxQjEwQWFCd3A1NFFrcGZKZzlQM3FxUSJ9;sgcookie=E1002T7lsa4260ak4m1sDfo6Fa79c2%2FCE3bO85pJyLNYr6KzykqcGHXwaUl%2BFMNH53P5xg%2B6lsrcmekFSE9bh4iFibPEBMs%2FUIdO4cRyEc3mJIE%3D;_tb_token_=f93febebe74e5;havana_lgc_exp=1763876520647;t=d16c294d7ffe8e9f6c338cdafbd2b9e5;_hvn_lgc_=77;_m_h5_tk=6d0f1f75c7a41d4a7cd5368a00261b35_1761297885409;_samesite_flag_=true;cookie2=1a4e584105bb57dac89defef1c96faa3;csg=9853ef97;tracknick=%E9%87%91%E5%85%89%E9%A3%9E%E8%B7%83;unb=1650607026'
    proxies = None
    asyncio.run(service.get_new_cookies(cookie_str, proxies=proxies)) 