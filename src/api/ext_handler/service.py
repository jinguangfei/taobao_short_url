import json
from shutil import which
import traceback
from re import I
import requests
import random
from typing import Union, Optional

from src.core.redis_script import redis_pool
from src.api.utils.func import (
    cookie_queue,
    get_taobao_tk,
    parse_cookie_str,
    get_mi_id,
    parse_url,
    build_url,
)

class CookieHandler(object):
    def __init__(self):
        self.redis = redis_pool
        self.cookie_key = f"handler:cookie"
        self.x5sec_key = f"handler:x5sec"

    async def handler(self, user_id : int, view_name : str = "chrome_ext", add_t : int = 12) -> Optional[dict]:
        cookie_info = self.redis.hget(self.cookie_key, user_id)
        if cookie_info:
            cookie_info = json.loads(cookie_info)
        else:
            cookie_info = await cookie_queue.get_one_info(view_name=view_name,add_t=add_t)
            if cookie_info:
                self.redis.hset(self.cookie_key, user_id, json.dumps(cookie_info))
                cookie_id = cookie_info.get("id")
                await cookie_queue.delete(cookie_id,view_name=view_name)
        # 获取tk
        if cookie_info:
            tk =  await get_taobao_tk()
            if tk:
                cookie_dict = parse_cookie_str(cookie_info["cookie"])
                tk_dict = parse_cookie_str(tk)
                cookie_dict.update(tk_dict)
                cookie_info["cookie"] = ";".join([f"{k}={v}" for k,v in cookie_dict.items()])
            x5sec = self.redis.hget(self.x5sec_key, cookie_info.get("id"))
            if x5sec:
                cookie_info["cookie"] = f"{cookie_info['cookie']};x5sec={x5sec.decode()}"
        return {"cookie": cookie_info}

class UrlHandler(object):
    def __init__(self):
        self.redis = redis_pool

    async def handler(self, ** kwargs) -> Optional[str]:
        item_id = kwargs.get("id")
        if not item_id:
            return {"url": ""}
        mi_id = await get_mi_id(item_id=item_id)
        print(mi_id)
        if not mi_id:
            return {"url": ""}
        mi_id_url = "https://" + mi_id if not mi_id.startswith("https://") else mi_id
        url_path, query_params = parse_url(mi_id_url)
        query_params.update(kwargs)
        result = {"url": build_url(url_path, query_params)}
        return result

cookie_handler = CookieHandler()
url_handler = UrlHandler()