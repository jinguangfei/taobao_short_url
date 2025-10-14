import json
import traceback
import time
from typing import Dict, Tuple, Optional
import hashlib
import urllib.parse
from curl_cffi.requests import AsyncSession
from curl_cffi.requests import Response
from src.loger import logger

def parse_cookie_str(cookie_str : str) -> dict:
    cookie_dict = {i.split("=")[0]:i.split("=",1)[1] for i in cookie_str.replace("; ",";").split(";") if len(i.split("="))>1}
    return cookie_dict

def parse_url(url: str) -> Tuple[str,Dict]:
    url_params = urllib.parse.urlparse(url)
    query_params = urllib.parse.parse_qs(url_params.query)
    for k, v in query_params.items():
        query_params[k] = v[0]
    url_params = url_params._asdict() # convert to dict 
    url_path = url_params.get("scheme") + "://" + url_params.get("netloc") + url_params.get("path")
    return url_path,query_params


def md5_data(tk: str, data_str : str = "", t : str = "", app_key : str = "12574478") -> Tuple[str,str]:
    t = t if t else str(int(time.time()*1000))
    app_key = app_key if app_key else "12574478"
    data = (r'%s&%s&%s&%s' % (tk,t,app_key,data_str)).encode("utf-8")
    m = hashlib.md5()
    m.update(data)
    sign = m.hexdigest()
    return t, sign, data_str

async def crawl(url: str, data: dict, tk: str, proxies: dict, headers: dict, cookies: dict) -> Optional[Response]:
    url, query_params = parse_url(url)
    data_str = json.dumps(data).replace(" ", "")
    t, sign, data_str = md5_data(tk, data_str, app_key=query_params.get("appKey"))
    query_params["data"] = data_str
    query_params["sign"] = sign
    query_params["t"] = t
    try:
        async with AsyncSession() as session:
            res = await session.get(url, headers=headers, params=query_params, timeout=10, cookies=cookies, proxies=proxies)
        return res
    except Exception as e:
        logger.error(traceback.format_exc())
        return None

async def get_mi_id(cookie : str = "", proxies : dict = {}, times : int = 5) -> str:
    url = "http://123.56.44.124:9460/api/mi_id/"
    for i in range(times):
        try:
            async with AsyncSession() as s:
                res = await s.post(url, json={"cookie":cookie, "proxies":proxies})
                return json.loads(res.text).get("result")
        except Exception as e:
            pass