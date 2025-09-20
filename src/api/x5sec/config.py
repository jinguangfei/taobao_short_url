from pydantic import BaseModel
from typing import Optional, Dict

class APIInfo(object):

    class Params(BaseModel):
        slide_url : str
        ua : Optional[str] = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36"
        cookies : Optional[Dict[str,str]] = {}
        cookie_str : Optional[str] = ""
        proxies : Optional[Dict] = {}
        body : Optional[str] = ""
        max_times : Optional[int] = 4

    url = "http://123.56.44.124:9478/ali227"
    headers = {
        "Content-Type": "application/json"
    }
    timeout = 12
    ua = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36"