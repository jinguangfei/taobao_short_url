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

    async def get_new_cookies(self, cookie_str: str, exclude_cookies = ["sgcookie"], proxies = None, timeout = 10, check_flag = lambda x: "sgcookie" in x) -> Tuple[ReloginFlag, str]:
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

    async def _get_new_cookies(self, cookie_str: str, exclude_cookies = ["sgcookie"], proxies = None, timeout = 10, check_flag = lambda x: "sgcookie" in x) -> Tuple[ReloginFlag, Dict[str, str], str]:
        """执行登录状态检查请求"""
        # 请求URL
        url = 'https://login.taobao.com/newlogin/hasLogin.do?appName=taobao&fromSite=77'
        url = 'https://ipassport.damai.cn/newlogin/hasLogin.do?appName=damai&fromSite=77'
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
            print(proxies)
            async with AsyncSession() as session:
                response = await session.post(url, headers=headers, data=data, cookies=cookies, proxies=proxies, timeout=timeout)
                print(response.text)
                print(response.headers)
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
    service = TaobaoReloginService()
    cookie_str = 'sn=;t=e1bba3faea87d9ab9984c14082995cee;existShop=MTc2MTg4Njk3Mg%3D%3D;cookie1=VAFbEzZ5ouu1uLV%2BljzdICw2BZD37nhFqmVjXk1uz2Y%3D;csg=d2d89d51;wk_cookie2=1eac26c0c64f0354484e32eb6b5f8840;cookie2=15b534a1330339b73cd1fdd8d274df9e;xlly_s=1;sca=e5da839a;skt=17da27fef228fb35;unb=2219200168501;_tb_token_=e4b9bde5ef38;sgcookie=E100mRGAND%2F1N8z4nGvrJ473GiTWAuAGXcBjvT%2BhMijpQKyJYqFfG%2B7VCNKXpQUMf7oNkLVIXIKgPY6v2Uvg35HVVlNVOmxSFlcTJYSi%2FmssJ%2FM%3D;aui=2219200168501;_samesite_flag_=true;cna=U8RPIRp5xA4CATwSGUPxPub2;tfstk=g4viIz_pIwa7ete_smXssGRzV1GpfO6fyEeAktQqTw7QWPe90iWD8En1Wnu6oKbe05e9HCFcgELH6sJAkKmcCpdTHN31nn8Rn43-eYK6fOXqy4p2f2ld3ikAuXCwUB73U43-evK6ft6qyh3-7XahqgWVbs5VLDjf8PWV7szUTg7Fut82uHoHKEff3t82YDjf8ZWV3E-E1ZENr_CeLq_mHqKULJJhj1buHw20nmIGsa-N-MsBLx1Gzh733Vkjtw7FqpubWZ9HYdSJ8veGnHSDrORn8RYDbQTf4Fk37GAwq3CHh4ycAB819GAn0W7w4N8GsQ4EjZ99SKf6U4eC7BvBnOdKS8QfgBp1Nd3UITRWXOd28myVoBSV4pNUaFNYhMovKSNf_MshyY-ayjE_obWrxDV7G1SCbnonxSZO_MshyDm3aECNAG-V.;wk_unb=UUpgT71fFLuseDWfkw%3D%3D;_cc_=VFC%2FuZ9ajQ%3D%3D;thw=xx;_m_h5_tk_enc=8327ee329689ce1d4c047cd6d5019af0;x5sec=7b2274223a313736313838363837392c22733b32223a2263626535663438373462306232666239222c22617365727665723b33223a22307c434a79466b636747454e54726f5044372f2f2f2f2f774561447a49794d546b794d4441784e6a67314d4445374d79494a5932467763485636656d786c4d4e2f2b3871762f2f2f2f2f2f77453d227d;isg=BAwM2w1ZiVshk5zufRo_uUPR3Ww-RbDvixXR8mbNGLda8az7jlWAfwJTk_lJouhH;3PcFlag=1761886970187;_hvn_lgc_=0;_l_g_=Ug%3D%3D;_m_h5_tk=c6f3302697e44b8ae784b4d379621d0d_1761889503390;_nk_=tb070465819509;cancelledSubSites=empty;cookie17=UUpgT71fFLuseDWfkw%3D%3D;dnk=tb070465819509;havana_lgc2_0=eyJoaWQiOjIyMTkyMDAxNjg1MDEsInNnIjoiMDQyNzZiNGUyYWRlMDJmOWMyYTUzY2RkZGNkZTFlMmYiLCJzaXRlIjowLCJ0b2tlbiI6IjFoWXRodmVQdHRiRGVHM0padDNwYVhBIn0;havana_lgc_exp=1792990972115;havana_sdkSilent=1761911104869;lgc=tb070465819509;sdkSilent=1761911104869;sg=91c;tracknick=tb070465819509;uc1=cookie16=UtASsssmPlP%2Ff1IHDsDaPRu%2BPw%3D%3D&pas=0&cookie14=UoYY4vPjzAYhsQ%3D%3D&existShop=false&cookie21=URm48syIZQ%3D%3D&cookie15=URm48syIIVrSKA%3D%3D;uc3=lg2=VT5L2FSpMGV7TQ%3D%3D&id2=UUpgT71fFLuseDWfkw%3D%3D&vt3=F8dD2kvzc82fZS%2FrwYw%3D&nk2=F5RFh66%2FzgFA2Ym0i9Q%3D;uc4=nk4=0%40FY4O7ocYlng%2BDvcN21RLDtMsMSvcxvd8EQ%3D%3D&id4=0%40U2gqwAJDC7n8nC%2FVCcyqYPh9YzoBclDz'
    cookie_str = '_m_h5_tk_enc=980989316014b4600054b96786120a2c;damai_cn_user=FeILrPxtgBVe%2BBtCHeYdcG8RnJJB3Wgk5ueIU1IoK64OvLFhUyR0QNn5h7IdMf6VGxb2%2BRjuqig%3D;user_id=482350416;csg=927b0eca;damai.cn_nickName=%E9%BA%A6%E5%AD%907o319;isg=BOfny7IaQvYNY8hmZGbil7Y8dh2xbLtOLLwqg7lULXadqAdqwTjWniWizqg2QJPG;tfstk=g79rizA3o9YXS54jFEBUbUH-VPBRd9u_ap_CxHxhVabuF8aHgFLFN0dWxwRFoTfpNw_589-p7mgsCAtJ29BS5VM6n-Lkh9Qnd9cfn7KNFz3sCAtoZgBBmVOWLuQ5vMXhq6blnmSFjzXh-MmVoMSTtzYhKmoVVM4uZMfkmrjhowXhKexm0M_cq9XH-nmVvfekKLcRv_mfDH9Zd5jGaNxluR-v3gjTw3b4KJv2g_7gFZy3KKSycYjvV8DNoQOHFtvooy6DXITl0OkUYiRwmTjyJAeREhxDt_JEOlQpgnA1gIES2iJybpSNixzcb1JDFTdq7R_MMHvFi33a6iOHfLOePqehPC-Du19blR6DUUJlgOjz7yIDh8ppayVFZiIV5moqNSB2c03ifZNL9sjA0NiulWFdZNsV5mo49WC-li7sqr1..;cookie2=1e964f2564deffa7d6cd5b33d1483641;_hvn_login=18;_m_h5_tk=1a8ae3da92d4a3b00ca6ee4bf3d0cfc5_1762143319396;_samesite_flag_=true;_tb_token_=e34bee1bf4353;damai.cn_user=FeILrPxtgBVe+BtCHeYdcG8RnJJB3Wgk5ueIU1IoK64OvLFhUyR0QNn5h7IdMf6VGxb2+Rjuqig=;damai.cn_user_new=FeILrPxtgBVe%2BBtCHeYdcG8RnJJB3Wgk5ueIU1IoK64OvLFhUyR0QNn5h7IdMf6VGxb2%2BRjuqig%3D;destCity=%u5317%u4eac;h5token=953893ccfb734d93961020a88057842a_1_1;loginkey=953893ccfb734d93961020a88057842a_1_1;munb=2217579181029;sgcookie=E100KitlBmbPuWy5Q9N%2F6InnnLb8NMMx%2BCk3kZg7H2kUghqoe6XZ31oBMGfsPJWhZm0YI7sbaPQKhrggsKcr5KFNXieAaB%2FzmEk0IvN%2BnGiSAwI%3D;t=9401a50361baa30259f610656861cde6;xlly_s=1;XSRF-TOKEN=acdc8a5d-d25f-496b-9932-b014a92c0bfe'

    cookie_str = cookie_str + ";last_cc=EDD840ABEE517462139AC69D0B129DDE;last_u_damai_damai=eyJoaWQiOjIyMTc1NzkxODEwMjksImxvZ2luSWQiOiIxODg5Mzg0ODQ0NSIsInNnIjoiMmZhZHNiOTliMWZhY2Y3ZTYzNzE1NDQ5M2Q5MWNiZWMzNGQyZiJ9;_hvn_login=18;havana_tgc=eyJjcmVhdGVUaW1lIjoxNzYyMTMzNzYyMjE4LCJsYW5nIjoiemhfQ04iLCJwYXRpYWxUZ2MiOnsiYWNjSW5mb3MiOnsiMTgiOnsiYWNjZXNzVHlwZSI6MSwibWVtYmVySWQiOjIyMTc1NzkxODEwMjksInRndElkIjoiMUR6eV9DajNMQ3NCVE50WnB3RkNsUncifX19fQ;x5sec=7b22733b32223a2265326135373032333738386137616366222c22617365727665723b33223a22307c434932506f4d6747454a6246342b3445476738794d6a45334e5463354d5467784d4449354f7a4569436d4e6863484e736157526c646a496f67415177316f32353267593d227d"
    proxies = None
    flag, cookies, cookie_str = asyncio.run(service._get_new_cookies(cookie_str, proxies=proxies)) 
    print(flag.value)
    print(cookies.keys())
    print(cookies.get("sgcookie"))