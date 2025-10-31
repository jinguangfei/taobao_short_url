import json
import time
from typing import List, Dict, ClassVar, Optional, Type, Any
from pydantic import BaseModel, Field
from datetime import datetime
from enum import StrEnum, Enum


api_headers = {
    'accept': '*/*',
    'accept-language': 'zh-CN,zh;q=0.9',
    'cache-control': 'no-cache',
    'pragma': 'no-cache',
    'sec-ch-ua': '"Not;A=Brand";v="99", "Google Chrome";v="139", "Chromium";v="139"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"macOS"',
    'sec-fetch-dest': 'script',
    'sec-fetch-mode': 'no-cors',
    'sec-fetch-site': 'same-site',
}
user_agent_list = [
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36",
]
html_headers = {
    "user-agent":"Mozilla/5.0(WindowsNT10.0;Win64;x64)AppleWebKit/537.36(KHTML,likeGecko)Chrome/87.0.4280.88Safari/537.36",
    "accept":"text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    "accept-language":"zh-CN,zh;q=0.9"
}
from ..ext.base.schemas import ExtFunctionOut

class WorkerInfo(BaseModel):
    cookie : str = ""
    proxies : Optional[Dict] = {
        "http":"http://LVMJTEaf:XW2zzQtS@122.228.200.202:19258",
        "https":"http://LVMJTEaf:XW2zzQtS@122.228.200.202:19258"
        }

class WorkerTaskInfo(BaseModel):
    task_id : str
    ext_function : ExtFunctionOut
    url : Optional[str] = None
    cookie : Optional[dict] = {}

    @property
    def main_params(self) -> dict:
        return json.loads(self.task_id).get("main_params",{})

class OverTaskInfo(BaseModel):
    task_info : WorkerTaskInfo
    result : Dict[str, Any]
    real_url : str
    ua : str