import time
from typing import List, Dict, ClassVar, Optional
from pydantic import BaseModel 

class APIInfo(object):

    class Params(BaseModel):
        item_id : str
        proxies : Optional[Dict] = {}

    url = "https://h5api.m.taobao.com/h5/mtop.gaia.nodejs.gaia.arkact.handler/1.0/?jsv=2.7.2&appKey=12574478&t=1761072273293&sign=e0ce288835def0d3415999049d1b5ea8&api=mtop.gaia.nodejs.gaia.arkact.handler&v=1.0&method=GET&data="