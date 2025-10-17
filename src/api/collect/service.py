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
from ..taobao_tk.service import TaobaoTkService
from src.core.redis_script import redis_pool
from src.api.utils.taobao_req import crawl, parse_cookie_str

class CollectService(object):
    def __init__(self):
        self.redis = redis_pool
        self.api_info = APIInfo
        self.taobao_tk_service = TaobaoTkService()

    async def build_url_prev(self, params: APIInfo.Params):
        headers = self.api_info.headers
        _proxies = {
            "http": APIInfo.proxy_url,
            "https": APIInfo.proxy_url,
        }
        _proxies = {}
        proxies = params.proxies or _proxies
        tk_cookie = self.taobao_tk_service.get_taobao_tk()
        cookies = parse_cookie_str(params.cookie+f";{tk_cookie}")
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
        return await crawl(self.api_info.collect_url, data, tk, proxies, headers, cookies)

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
        return await crawl(self.api_info.item_list_url, data, tk, proxies, headers, cookies, **kwargs)

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
        result = [i.get("favId")+" "+i.get("itemUrl").replace("//","") for i in item_list]
        return flag, result

if __name__ == "__main__":
    service = CollectService()
    cookie = "t=6f06bf453bad0075802cd9a89edb929b;fastSlient=1760639242068;existShop=MTc2MDY0MTAxMA%3D%3D;cookie1=WqItotoTeMqUnOrd82i8UM7fNNavXrnN%2FCteV0EJZGM%3D;csg=ab48a8f8;wk_cookie2=1bec5621c1e7da519787e4cbdede7bfc;cookie2=10b709e42289414562b44e01a3c3de08;xlly_s=1;sca=e8b9cd3a;skt=264ef6026d88f2ed;unb=2219000715463;_tb_token_=e335efddd43d6;sgcookie=E100%2B3%2FpoUK%2BeY4VlNZiNxwQ0lBh6mUT46WJMYfUmgdbB7rYBPH7mM9%2BmKD%2Bs8fremuzBgkStXdUb%2FUn33dqwNU%2FX0wHAPjuA0g7WfKXjU82oHk%3D;aui=2219000715463;_samesite_flag_=true;tfstk=gmbtIJ9lXWhta9MZ6tq3oOENXKN3rkfZvO5SoKvic9BdN_kMcKqNHnBcLn_MS1XdG_fVn1V2mEQAEpXmo1Xm_MWlNVbgbE0v7E8bE84urf5wuEgqlF_MQ61eGWAsOjspaE8bEJ4ur15wuOOHbMbsAB9eMIOXft1Q9CJI5Ig6GvNpgpTXlE6fYEQpdKTXlt1Q9IJBhETXyOZ9dJvrkGw4HZt5Zp3jlwd_3L19pBRFJCK9FzJKkf7p6hp51advWrdAVaKNFJmMCgIceQXgRVBR1OIWVNMQpE5h2tdR57iJHO5CSH__i0ReuGsW5Ze-C6-RRNYNv83kFM5fkH1ae0Rhc_bGDO2EldjRO9Kl-v0kRNBO5HL54wQly11IELdmXWFK0m-6TUigCAERyYew9LVT6mo2vOdpEWeS0m-6TBputpiq0HCh.;wk_unb=UUpgT78RxJVLp%2BrzSQ%3D%3D;_cc_=V32FPkk%2Fhw%3D%3D;thw=cn;_m_h5_tk_enc=1cdd51b59865869b6907c644ff53dc72;isg=BDs7zqb917N0PesdESaYPMQbyhmlkE-ScFgGBy34EDpRjFtutWT24-BepCzCt6eK;3PcFlag=1760640999893;_l_g_=Ug%3D%3D;_m_h5_tk=64d0faf7603ceb1be6e6da6f829f24ee_1760652142381;_nk_=tb659477183;cancelledSubSites=empty;cookie17=UUpgT78RxJVLp%2BrzSQ%3D%3D;dnk=tb659477183;lgc=tb659477183;sg=333;tracknick=tb659477183;uc1=cookie14=UoYY4%2F1DsnCBaQ%3D%3D&cookie16=UIHiLt3xCS3yM2h4eKHS9lpEOw%3D%3D&existShop=false&pas=0&cookie21=U%2BGCWk%2F7og%3D%3D&cookie15=UtASsssmOIJ0bQ%3D%3D;uc3=id2=UUpgT78RxJVLp%2BrzSQ%3D%3D&lg2=V32FPkk%2Fw0dUvg%3D%3D&vt3=F8dD2ky%2BozXyMyvS2C8%3D&nk2=F5RDKXxU%2BvUbMYA%3D;uc4=nk4=0%40FY4I6gjTB9qJHkVX8Wu09Hr4eidYDA%3D%3D&id4=0%40U2gqwAAtIxOHqVhzWHPbnhpsqTyDGXf7"
    cookie = "ucn=eleme_zb;__ebg_uid=2836215;USERID=2836215;xlly_s=1;xqkp=T2gAFuJetl58srdvdkDcZVHrR6v6ybVS-iScdAmdG6fE6NTOsVEURMUk8N32pPhizMA=;t=b84881e9fe5a22a22423751442be7449;SID=MTI0MTA1MDMzNjY3NjE2NTEzZjFiZDExZjU3MGQ5NjllTh7SRApyJ9xYVEqhnh2ymA==;unb=2204184550106;tfstk=gX9q5dZd3OY5EVbAiL6a46_hfUXALOuISd_1jhxGcZb0hjHwQFTViEsXGGyNzeW6GhxbQU7koSbDcNTwja8NC-gvjRowRURfsnOX_A86jN1iktiZbeTTCn9wXRSMjFnA5mhWDnBOI2gBQvtvDjnRs805IcxlCGyIikI2DnBT2uaiOQxYblOEgtXMSTfljiWgn1YGZYbRXG4cj-mr4aI_iRXGj8DlDMbGIOYMq0SOriXGiFxkrF9MnjIOi0lIgDM4sgCV-nbzL3pPm1NvmaygILRPgwv1zR2MUi-aHxt0nv7kGCvfEK0uJTxpNEjPLArN4B-lni8tp-BDx3AGgdl_vNdyqB1ywoiA4K-eQM58rm79hEJNMp0QeZAyedWXNqyCW1AWH6pjr-WH9n6XsUmgINRljg70Wg0j4dd4S5fc2g7I40lbwT-Sx1JMN5FOZgIPRm4765Cc5g7I40PT6s3P4wi00;_samesite_flag_=true;perf_ssid=jgcruimwlcxf7t9mobtpk1il34555nzb_2025-10-17;sgcookie=E10091gQlIBSs73PzPWcmdn6DwFpjSk7Veeuf3CMEL%2BEDQuGGpLmK2qrx4FncTouKqV%2B5JFYEx5c7t%2FUaAOx0oKfR%2FlDqrvzRDUtG7aWa1m31nU%3D;__ebg_utdid=ad7b479f-581c-4358-ceb4-af4861847ea3-1760555085554;_bl_uid=FgmawgLbtUvv85fdO4hUf8a45tOU;_tb_token_=f3339355bfeb1;cookie2=124105033667616513f1bd11f570d969e;isg=BOPj1ziXjzv0iEMR9TwXH4euciGN2HcaiJCuDxVAO8K5VAN2naknan4HSiTadM8S;munb=2204184550106;ubt_ssid=vn7i1zxkuxur06p787xmkx3kza88cnqp_2025-10-17;UTUSER=2836215"
    cookie = "ucn=eleme_zb;__ebg_uid=2836215;USERID=2836215;xlly_s=1;xqkp=T2gAFuJetl58srdvdkDcZVHrR6v6ybVS-iScdAmdG6fE6NTOsVEURMUk8N32pPhizMA=;t=b84881e9fe5a22a22423751442be7449;SID=MTI0MTA1MDMzNjY3NjE2NTEzZjFiZDExZjU3MGQ5NjllTh7SRApyJ9xYVEqhnh2ymA==;unb=2204184550106;tfstk=gdWtCyTl6kntUFgZXZV3nNE7IyZ3tWjaSNSSnEYiGwQd73dfsZqN9tQk8CjGm1YbHg7J5ZI4bnTflZLcsW2lbGJ2hzbYE8jahAHINOpjoM9wmyMKGN2lbGoIXqZlO8mv1_0klE_X1eOBmeMj1ZT6AkKXmVGjCZsQve-DccOXcDGBDnx6hK_fAkK2RE9X1ZsQvn8BlUC36eaHzxC_uJV4_F8Khx6pfr85XeKeY9K96UOBJxiGphd9PG6J8XJXD_6J_aansF1RiaKlSJMOyG_ONQ6sRypVx_Qv2OZSwEQNAOACCocyYK51Nd6YyVsew96MQ6U-EU1FctdCbzhyxsslIsQg8xTGwM_pZ90nEp6OWOOpFg8lETI1A4YJmfZLvjl21HJSsPgO_CzuAHLuXlhqgBQ9vUqLljl21H-prkYIgjRdx;_samesite_flag_=true;perf_ssid=jgcruimwlcxf7t9mobtpk1il34555nzb_2025-10-17;sgcookie=E10091gQlIBSs73PzPWcmdn6DwFpjSk7Veeuf3CMEL%2BEDQuGGpLmK2qrx4FncTouKqV%2B5JFYEx5c7t%2FUaAOx0oKfR%2FlDqrvzRDUtG7aWa1m31nU%3D;__ebg_utdid=ad7b479f-581c-4358-ceb4-af4861847ea3-1760555085554;_bl_uid=FgmawgLbtUvv85fdO4hUf8a45tOU;_tb_token_=f3339355bfeb1;cookie2=124105033667616513f1bd11f570d969e;isg=BF9fYxtRS-forU_lEZDTU2ua7rXpxLNm9OSiG_Gs-45VgH8C-ZRDtt3TRhD-GIve;munb=2204184550106;ubt_ssid=vn7i1zxkuxur06p787xmkx3kza88cnqp_2025-10-17;UTUSER=2836215;sn=;t=f78858d61438e08afa6ee408fcf7f4d8;existShop=MTc2MDU1MTA4MQ%3D%3D;cookie1=UUHwg%2FS5WnhNI9amMIJ99KjIP87Gan0TQSnhlgp7604%3D;csg=fbca8153;cnaui=2219000715303;;xlly_s=1;sca=d898b3c8;skt=405729e35da396e1;unb=2219000715303;_tb_token_=e4bbbee853e78;aui=2219000715303;_samesite_flag_=true;tfstk=g9nKzTNmJdBK4P5FpbYMq2hoPfJgpFDEQXkfq7VhPfhtTxFnqkDlwVHqwWvy8k0TwfGTO6qhxfE81bnhqkNu2bFsGpknZwf8PfMYZWa7OGM_K5y5VWZ5CfEEj2jutBr-FjqJiIxDmvkUYuODiR_0gyqb38wCZz615u2-OuHB_vkU4OWGNE0sLTBokJQ7F79Tf8wlAua5AO___8bQNbNQ51wY3uNSNbZ11-wQd7wQF1s__8Z7dbNCCGNaFuwINu9tC5yS_k8L1CVV22OSRDCyVwZU2ceLJSM9uMICl5C0sv61DintWgeSdqs5VceLRcTb7N_bV2Mn6r0pMMEmdqlzhX1B9RnKH03j1hjL2Agj2li61OVIuAn8xD9kAliK9DatNTbgRqlnlPnM9GPj5AHuWVJP-704FbzqqISUOYMq0qqv2TetkAZO4TomDvM1iSelRdpOzazQQo_HO6d57G4_BSvppa7zWXeTidd5zazQQRFDI5_PzPHG.;wk_unb=UUpgT78RxJVLp%2B1YLw%3D%3D;_cc_=URm48syIZQ%3D%3D;thw=cn;isg=BBoapOg9JuQVLqpQzM45DU5xa8Y8S54lKTMHiCSZ2qXWl7DRBdk_NP4kY2MLRxa9;3PcFlag=1760551079089;_hvn_lgc_=0;_l_g_=Ug%3D%3D;_nk_=tb4268570497;cancelledSubSites=empty;cookie17=UUpgT78RxJVLp%2B1YLw%3D%3D;dnk=tb4268570497;havana_lgc2_0=eyJoaWQiOjIyMTkwMDA3MTUzMDMsInNnIjoiZjMxMTc4ZGM4Y2U0N2Q1MDdhZjk4NzIxOThlMDllYzMiLCJzaXRlIjowLCJ0b2tlbiI6IjE4TktlVFBqRDR2U1lyN2pkTm9iV3pRIn0;havana_lgc_exp=1791720073337;havana_sdkSilent=1760644573827;lgc=tb4268570497;sdkSilent=1760644873337;sg=73c;tracknick=tb4268570497;uc1=pas=0&cookie15=W5iHLLyFOGW7aA%3D%3D&cookie16=W5iHLLyFPlMGbLDwA%2BdvAGZqLg%3D%3D&cookie21=W5iHLLyFfA%3D%3D&cookie14=UoYY4%2F5IWkNniw%3D%3D&existShop=false;uc3=vt3=F8dD2ky996xrFtNHwPA%3D&id2=UUpgT78RxJVLp%2B1YLw%3D%3D&lg2=U%2BGCWk%2F75gdr5Q%3D%3D&nk2=F5RBx%2BY1l9RBu6UP;uc4=nk4=0%40FY4KoqYDMOMGWq7%2F%2BBtGDXWhCKLXPBA%3D&id4=0%40U2gqwAAtIxOHqV88D0L5NwuGKiF%2BQ%2Fe2"
    cookie = "sn=;t=7fa9c947f3bc49142f4a8f418e838a2d;fastSlient=1760712223917;existShop=MTc2MDcxMTgzMg%3D%3D;cookie1=AiTwBgtZeY6XStUtqAsWIy%2BVFq6ONPDvp6AdHcPmjgI%3D;csg=22c0eae2;wk_cookie2=1578737db65b0118e4e31cff571d8716;cookie2=11eeb8767ca5a2036b5d40361b3abd3d;xlly_s=1;sca=712b7624;skt=0b4fe4c191b201f6;unb=2218983283748;_tb_token_=e375e386eb3a6;sgcookie=E100OM7nEzPgtiaUn3YXUFD2txGTZmdQ0OC%2B0tjTJoRR0%2F793eTiLPp3ALEQ2uLF%2BpVwZPhqOpe4mRpudaa5dm7UgFMxdOVJ3U8JGl0m1Fvt4Ws%3D;aui=2218983283748;_samesite_flag_=true;tfstk=gaZSC9taFWE2Q94tPDW2lVl6CNnQ2tSwVpMLIJKyp0nJ9BetgHWo4wmQOjNna4o8ArxQIJqPEDWoq8mnv15NbkwuEDf0YmrCg-BKKDM8bCwk68mnv1J2vNS_E7ve-KlKpxBjLvJJJW3JkjHIMvL-vWhxkAHwwDnL9tGxBALJw4HJkmHoMXnKvWeAhvcxeDnL9-BjKUjecvtmg86tLwO1gHn4ejtpvuInPfZk8HKLcYg7vShfL9rjF4GtJEbODlwTelDQxOLIOJz8axVCfsiYV7Z-lDsBm0y_k7gbP6tjoregvqac1F2ge7atWuIfnWNYIPm826xrZyeYvjrRLHGT7Rmjnk5D2XaYJuuoxQCShuw_AysrUhlsa9TBhVxIhfWfheYnOHc8s_HrWPu-nYGNhtTNF4HmhxXfheYnyxDVBt6X7w5..;wk_unb=UUpgTsA4z9%2Bag1MhSg%3D%3D;_cc_=W5iHLLyFfA%3D%3D;thw=cn;_m_h5_tk_enc=1f22855eff4cad6479a7d0511794a843;isg=BMTEsflgcEUMCMQJ2k_pOGrZlUS23ehHk_1pyt5ldA9SCWTTBu6Q161jSaHRESCf;3PcFlag=1760712223911;_l_g_=Ug%3D%3D;_m_h5_tk=7cf5152f8154c20a5c479f7abb1e2eca_1760720704945;_nk_=tb5981563415;cancelledSubSites=empty;cookie17=UUpgTsA4z9%2Bag1MhSg%3D%3D;dnk=tb5981563415;lgc=tb5981563415;sg=58e;tracknick=tb5981563415;uc1=cookie21=WqG3DMC9EA%3D%3D&cookie15=V32FPkk%2Fw0dUvg%3D%3D&cookie16=U%2BGCWk%2F74Mx5tgzv3dWpnhjPaQ%3D%3D&cookie14=UoYY4%2FxQxd2s8Q%3D%3D&pas=0&existShop=false;uc3=id2=UUpgTsA4z9%2Bag1MhSg%3D%3D&lg2=WqG3DMC9VAQiUQ%3D%3D&nk2=F5RAS6ujdjqLFeBy&vt3=F8dD2ky%2FIqUF76N581k%3D;uc4=nk4=0%40FY4L52g%2BzNg4TTBpNtXU987HlVDyp7U%3D&id4=0%40U2gqwYnxQG%2FXujxewXNpCTCRy5avIizW"
    with open("src/tmp/need","r") as f:
        item_id_list = f.readlines()
        item_id_list = [i.strip() for i in item_id_list]
    #params = APIInfo.Params(targetId="", cookie=cookie, proxies={})
    #res = asyncio.run(service.item_list_url(params))
    #flag, result = service.check_item_list_body(params=params,body=res.text)
    #with open("src/tmp/t4","a") as f:
    #    f.write("\n".join(result)+"\n")
    #time.sleep(10000)
    with open("src/tmp/t4","r") as f:
        have_list = f.readlines()
        have_list = [i.strip() for i in have_list]
        have_id_list = {i.split(" ")[0] for i in have_list}
    print(len(item_id_list))
    item_id_list = [i for i in item_id_list if i not in have_id_list]
    print(len(item_id_list))
    for i in range(1):
        for item_id in item_id_list[200*i:200*(i+1)]:
            params = APIInfo.Params(targetId=item_id, cookie=cookie, proxies={})
            res = asyncio.run(service.collect_url(params))
            print(res.text)
            time.sleep(4)
        res = asyncio.run(service.item_list_url(params))
        flag, result = service.check_item_list_body(params=params,body=res.text)
        with open("src/tmp/t4","a") as f:
            f.write("\n".join(result)+"\n")
        #print(flag, len(result))
