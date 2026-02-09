import base64
import time
import json
import asyncio
import hashlib
import traceback
from typing import Tuple,Dict,Any
import urllib.parse
from curl_cffi.requests import AsyncSession
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

def parse_cookie_str(cookie_str : str) -> dict:
    return {i.split("=")[0]:i.split("=",1)[1] for i in cookie_str.replace("; ",";").split(";") if len(i.split("="))>1}

async def get_proxies(queue : MyQueue = shanchen_queue) -> dict:
    recv_dict = await queue.get_one_info(add_t=20)
    print(recv_dict)
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
        "cookie": "ucn=eleme_zb;__ebg_uid=1667064753;USERID=1667064753;xlly_s=1;xqkp=T2gAMVUlAR5nXFkYqDOG-AZSjog5mQ80hFk80llYkhfRrdDdn6v4OaB-3hWGaCTES7g=;t=22eb1b7f35e030b02b1511a343091cc2;SID=MWJjMGU3YWM1NWQ4NDQ1NTc0ZWY2OWU5OGUxYzdhOTdltGc7x4i-XLkyXv9HG7uRIw==;unb=2205126579780;tfstk=ghet5G0arMK9HYetxl5hiHiw02Shq6qaYPrWnq0MGyULVrEis1PgpEEuW-VgcGSvH2ULsVM_npaL-ugioo1NDqaj-5DcblvY9y4tilfZnoNL7ylgsxfwkKHaK5vmSNkYczDAraXlElrZBx_lrsfSuzHjct0ftfaGciSAraXlK1tIHNQuja2scwnqRcij5CsKRm3BCcaj5XTI20kjhrG6O9ixmmTsfm6CvmuIlxMblksKm2gjsrftRw0yH5r-HFYwA3JWFJnt6qpmJKp5mchtklgdPawdhf37f2pfzh5xS2i8dZ8iuJEQC04CKdHYAmU-CWQBBrE_aro759LsX5Z8qXeVPKnUOPlnXWIXOVZS5PhTwestuR4THfy5rpu_9JyxIWb9EqlbtRlzIw9tF7riISaCcKgYOmsPf828FpYoymAOvMd2gfiEFCb6WUsFEsiKrGI9gIlLWD3lvaO2gfiEv4jn8IRq9PC..;_samesite_flag_=true;sgcookie=E100Ie9jsrDmwCX%2FTgK2EP8LsMi%2Fp9EYcbiI4V1kDMuQvKMIX%2FlGhWVgZMHkeqmdlAWWEXwS0kcuph9p66RqL5%2FqAirjcD2WF4F%2FLpRznh9NYiskdqEouENtVDP2UDO3gUqq;__ebg_utdid=1bd96c41-3061-421c-e28b-b768d639f725-1729478361143;_tb_token_=f53bf33f0839;cna=Bl+KIfDBFWsCAQAAAACS/MyN;cookie2=1bc0e7ac55d8445574ef69e98e1c7a97e;isg=BAMDdMrdbm7mGy_YtQqm6yLnksGteJe66PDOrzXg-mLZ9CcWtkqaC2knboS61O-y;munb=2205126579780;UTUSER=1667064753",
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

def parse_base64_img(img: str) -> bytes:
    data_str = img.strip()
    if data_str.startswith("data:"):
        comma_index = data_str.find(",")
        if comma_index != -1:
            data_str = data_str[comma_index + 1 :]
    return base64.b64decode(data_str)
if __name__ == "__main__":
    #print(asyncio.run(get_proxies()))
    with open("/Users/duchunxing/a","r") as f:
        img = f.read()
    with open("a.png","wb") as f:
        f.write(parse_base64_img(img))