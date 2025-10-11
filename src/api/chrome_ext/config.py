import time
from typing import List, Dict, ClassVar, Optional, Type
from pydantic import BaseModel, Field
from datetime import datetime
from enum import StrEnum, Enum

main_query_fields = ["ttid"]
TAOBAO_CONFIG = {
        "name": '淘宝详情',
        "type": 'network',
        "domain": '.com',
        "url_whitelist": ['mtop.taobao.pcdetail.data.get','item.htm'],
        "url_blacklist": ["_____tmd_____"],
        "body_whitelist": ['sku2info','punish?x5secdata','action=deny','pureDenyWait='],
        "body_blacklist": ['FAIL_SYS_TOKEN',],
        "web": True,
        "timeout": 12,
        "break_flag": ["login","deny"]
    }
LT_TAOBAO_CONFIG = {
        "name": '陶特详情',
        "type": 'network',
        "domain": 'taobao.com',
        "url_whitelist": ['mtop.taobao.ltao.detail.h5.data.get'],
        "url_blacklist": ["_____tmd_____"],
        "body_whitelist": [],
        "body_blacklist": ['FAIL_SYS_TOKEN',],
        "web": True,
        "timeout": 12,
        "break_flag": ["login","deny"]
    }
config_dict = {
    "LT_TAOBAO" : LT_TAOBAO_CONFIG,
    "TAOBAO" : TAOBAO_CONFIG
}


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

class TaskType(StrEnum):
    TAOBAO = "TAOBAO"
    LT_TAOBAO = "LT_TAOBAO"



class TaskInfo(BaseModel):
    item_id : str
    task_type : TaskType = TaskType.LT_TAOBAO
    # 当前日期
    batch : Optional[str] = Field(default_factory=lambda: datetime.now().strftime("%Y%m%d"))
    timeout : int = 10

    @property
    def uniq_id(self) -> str:
        return f"{self.batch}____{self.item_id}____{self.task_type}"
    
    @classmethod
    def gen_by_uniq_id(cls, uniq_id : str) -> tuple[str, str]:
        batch, item_id, task_type = uniq_id.split("____")
        return cls(batch=batch, item_id=item_id, task_type=task_type)

    @property
    def url(self) -> str:
        return f"https://main.m.taobao.com/app/ltao-fe/we-detail/home.html?&id={self.item_id}"

class WorkerInfo(BaseModel):
    cookie : str = ""
    proxies : Optional[Dict] = {
        "http":"http://LVMJTEaf:XW2zzQtS@122.228.200.202:19258",
        "https":"http://LVMJTEaf:XW2zzQtS@122.228.200.202:19258"
        }

class WorkerTaskInfo(BaseModel):
    task_info : Optional[TaskInfo] = None
    short_url : Optional[str] = None
    config : Optional[dict] = config_dict[TaskType.LT_TAOBAO]
    cookie : Optional[dict] = {}
    flag : str
    
    @property
    def url(self) -> str:
        return f"https://main.m.taobao.com/app/ltao-fe/we-detail/home.html?&id={self.item_id}"

class OverTaskInfo(BaseModel):
    task_info : TaskInfo
    cookie : dict
    result : str
    real_url : str
    ua : str

    @property
    def url(self) -> str:
        return f"https://main.m.taobao.com/app/ltao-fe/we-detail/home.html?&id={self.task_info.item_id}"

class APIInfo(object):
    TaskInfo = TaskInfo
    WorkerInfo = WorkerInfo
    WorkerTaskInfo = WorkerTaskInfo
    OverTaskInfo = OverTaskInfo

    short_url_api = "http://123.56.44.124:9460/api/short_url/"
    headers = api_headers
    url = "https://main.m.taobao.com/app/ltao-fe/we-detail/home.html?&id={item_id}"
    level = 100
    flag_score = {"slide":2,"deny":3,"deny2":3,"login":4,"success":1,"xiajia":1,"noitem":1}
    add_time = 8
    max_use_times = 1570
    max_use_sleep_time = 60 * 60 * 24
    slide_time = 60 
    deny_time = 60 * 30
    login_time = 60*60*24*7

    class ShortInfo(BaseModel):
        short_url : str
        long_url : str
        item_id : str
        target_url : str
        unb : str
        t : str