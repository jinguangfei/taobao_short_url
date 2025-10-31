import time
from typing import List, Dict, ClassVar, Optional, Type
from pydantic import BaseModel, Field
from datetime import datetime
from enum import StrEnum, Enum

PC_DETAIL = {
        "name": "pc详情",
        "type": "network",
        "domain": ".",
        "url_whitelist": ["mtop.taobao.pcdetail.data.get","noitem","item.htm",".hk"],
        "url_blacklist": ["_____tmd_____"],
        "body_whitelist": ["login.htm","sku2info","punish?x5secdata","action=deny","pureDenyWait=","noitem"],
        "body_blacklist": ["FAIL_SYS_TOKEN"],
        "ext_function": ["crawl"],
        "timeout": 8,
        "break_flag": ["login","deny"]
    }
LT_DETAIL = {
        "name": '陶特详情',
        "type": 'network',
        "domain": 'taobao.com',
        "url_whitelist": ['mtop.taobao.ltao.detail.h5.data.get'],
        "url_blacklist": ["_____tmd_____"],
        "body_whitelist": [],
        "body_blacklist": ['FAIL_SYS_TOKEN',],
        "web": True,
        "timeout": 8,
        "break_flag": ["login","deny"]
    }

ext_function_dict = {
    "PC_DETAIL" : PC_DETAIL,
    "LT_DETAIL" : LT_DETAIL
}