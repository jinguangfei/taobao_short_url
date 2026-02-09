import time
import json
import asyncio
import hashlib
import traceback
from typing import Tuple, Dict, Any, List
import urllib.parse
from curl_cffi.requests import AsyncSession
from curl_cffi.requests import Response
from .cls import MyQueue, shanchen_queue, cookie_queue


def parse_url(url: str) -> Tuple[str,Dict]:
    url_params = urllib.parse.urlparse(url)
    query_params = urllib.parse.parse_qs(url_params.query)
    for k, v in query_params.items():
        query_params[k] = v[0]
    url_params = url_params._asdict() # convert to dict 
    url_path = url_params.get("scheme") + "://" + url_params.get("netloc") + url_params.get("path")
    return url_path,query_params

def build_url(url_path: str, query_params: Dict) -> str:
    query_params_str = urllib.parse.urlencode(query_params, doseq=True)
    return url_path + "?" + query_params_str

def parse_cookie_str(cookie_str : str, exclude_cookies : List[str] = [], filed_seq : str = ";", name_seq : str = "=") -> Dict[str, str]:
    cookie_str = cookie_str.strip().replace(' ', '')
    cookies = {i.split(name_seq)[0]:i.split(name_seq,1)[1] for i in cookie_str.split(filed_seq) if len(i.split(name_seq))>1}
    for k in exclude_cookies:
        cookies.pop(k, None)
    return cookies

def parse_set_cookies(response: Response) -> Dict[str, str]:
    """
    解析响应中的Set-Cookie头
    """
    set_cookie_list = response.headers.get_list('set-cookie')
    set_cookie_list = [i.split(";",1)[0] for i in set_cookie_list]
    set_cookie_dict = {k:v for k,v in [cookie.split("=", 1) for cookie in set_cookie_list if "=" in cookie]}
    return set_cookie_dict

async def get_proxies(queue : MyQueue = shanchen_queue) -> dict:
    recv_dict = await queue.get_one_info(add_t=20)
    if not recv_dict:
        return None
    else:       
        return {
            "http": f"http://{recv_dict.get('proxy_ip')}:{recv_dict.get('proxy_port')}",
            "https": f"http://{recv_dict.get('proxy_ip')}:{recv_dict.get('proxy_port')}",
        }
    
async def get_mi_id(item_id: str) -> str:
    url = "http://123.56.44.124:9460/api/mi_id/"
    proxies = await get_proxies()
    data = {
        "item_id": item_id,
        "proxies": proxies,
        "cookie": "ucn=eleme_zb;__ebg_uid=1667064753;USERID=1667064753;xlly_s=1;xqkp=T2gAXwPP8rEXmlBhRe9xsljSrMXo8ujTikBzJpUMJWnsHPnu35Tax3e3i3uETvOMEt0=;t=c0200f1322999017a3c0ab18e5e47727;SID=MjUyNjYzMDM0Yzc3NDg2YzIxODM0OGU3MzgyZjNjMWZlMUl8PYAsMCjTotSzf3jUUQ==;unb=2205126579780;tfstk=gQJo5H_vEZa6yTgAMK6SZMgYdJlYNT6BLeedJ9QEgZ7by0OJ29DhkFNJ22iWiJYXS65-VT80xGQfwJBRpIXHlH9RT0TLKpYOk_KJvQBHYH_veaLpJJbHfUYhO0_d8wYpYQnxBAKWV96exVHtBlXoxvJl8yBFFtr1mfNoBAKW4uIrXnk9wa1JKa_FL_5Fux7fAgWFTJocuMj_Tz8e8mbVVMezU97FunSRuwWFLe-qmM_V49WE65qPS1C232_8NZ5M5Fvcq_bwqfwUKK2OZN-PoJuwng0C7370LJ7-hDf6Yeu3pOR6opfwRv2fehAV3gAmYS7PsQ8RceDgUaJD4L7JUqeRzLt26pLqYJ7HgC5GjKor__R6yC5DH42f7I-DvsAjA7Qp1M8C1p3_Fa-efdOOIvqhmCxVngWgg5879JsqvKVQO_SfmNHw4PhdFegIEmm01W1Pcg-EmmVQ2_SfmNnmm58OaisyY;_samesite_flag_=true;sgcookie=E100qdZakaH5CBxiyBDGdgoi7wubQJrZT2rDCH7ndFGBV6qg3JfLLu8nudRwtMv5mIHmCNdi71BSrYfDJJ4fYDTtns4KPCTyI0ZZC47wP5q7w9I%3D;__ebg_utdid=1bd96c41-3061-421c-e28b-b768d639f725-1729478361143;_tb_token_=e8a137fb8e6ee;cna=6lzTILKF/ngBASQIggdjCwMk;cookie2=252663034c77486c218348e7382f3c1fe;isg=BHR0oeKooaSLSTitLt9ZltmqRTTmTZg34405Og7V1P-CeRLDMV_OxqB6-bGhgdCP;munb=2205126579780;UTUSER=1667064753",
        "headers": {},
    }
    async with AsyncSession() as session:
        response = await session.post(url, json=data)
        return response.text

async def get_taobao_tk() -> str:
    url = "http://123.56.44.124:9460/api/taobao_tk/"
    async with AsyncSession() as session:
        response = await session.get(url)
        return response.text

async def get_source(name: str = "xianyu_cookie", add_t: int = 1, expire_time: int = 56, times: int = 5) -> str:
    url = f"http://123.56.44.124:9460/api/source/?name={name}&add_t={add_t}&expire_time={expire_time}"
    for i in range(times):
        async with AsyncSession() as session:
            response = await session.get(url)
            recv_dict = response.json()
            if recv_dict.get("data"):
                return recv_dict.get("data")
        await asyncio.sleep(1)

async def wait_source(id: int, add_t: int):
    url = f"http://123.56.44.124:9460/api/source/wait"
    cur_t = int(time.time())
    data = {
        "id": id,
        "add_t": cur_t + add_t
    }
    async with AsyncSession() as session:
        response = await session.post(url, json=data)
        return response.text

async def update_source_status(id: int, status: int):
    url = f"http://123.56.44.124:9460/api/source/status"
    data = {
        "id": id,
        "status": status
    }
    async with AsyncSession() as session:
        response = await session.post(url, json=data)
        return response.text

def md5_data(tk: str, data_str : str = "", t : str = "", app_key : str = "12574478") -> Tuple[str,str]:
    t = t if t else str(int(time.time()*1000))
    app_key = app_key if app_key else "12574478"
    data = (r'%s&%s&%s&%s' % (tk,t,app_key,data_str)).encode("utf-8")
    m = hashlib.md5()
    m.update(data)
    sign = m.hexdigest()
    return t, sign, data_str

async def get_x5sec(slide_url : str, ua : str, cookie : Dict[str,Any], proxies : Dict[str,str]={}, body : str="", **kwargs) -> str:
    x5sec = ""
    for i in range(4):
        try:
            data = {"url":slide_url,"ua":ua,"cookie":cookie,"proxies":proxies,"body":body}
            api_url = "http://123.56.44.124:9478/ali227"
            async with AsyncSession() as session:
                res = await session.post(api_url, data=json.dumps(data), timeout=12, headers={'Content-Type': 'application/json'})
            recv_dict : Dict = json.loads(res.text)
            if recv_dict.get("code")==0:
                x5sec = recv_dict.get("x5sec") if recv_dict.get("x5sec") else ""
                break
        except Exception as e:
            pass
    return x5sec
if __name__ == "__main__":
    print(asyncio.run(get_proxies()))