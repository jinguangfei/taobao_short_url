import time
from typing import List, Dict, ClassVar, Optional
from pydantic import BaseModel 

class APIInfo(object):

    class Params(BaseModel):
        cookie_str : str
        proxies : Optional[Dict] = {}

    url = "https://passport.goofish.com/newlogin/hasLogin.do?appName=xianyu&fromSite=77"
    headers = {
        'accept': 'application/json, text/plain, */*',
        'accept-language': 'zh-CN,zh;q=0.9',
        'bx-v': '2.5.22',
        'content-type': 'application/x-www-form-urlencoded',
        'referer': 'https://passport.goofish.com/mini_login.htm?ttid=h5%40iframe&redirectType=iframeRedirect&returnUrl=https%3A%2F%2Fh5.m.goofish.com%2Fapp%2Fvip%2Fh5-webapp%2Flib-login-message.html%3Forigin%3Dhttps%253A%252F%252Fh5.m.goofish.com&appName=xianyu&appEntrance=web&isMobile=true',
        'user-agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 16_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.6 Mobile/15E148 Safari/604.1'
    }
    timeout = 10