from typing import Optional
from pydantic import BaseModel
CONFIG_DATA = {
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
class LTParams(BaseModel):
    item_id : str
    cookie : str
    short_url : str
    config : Optional[dict] = CONFIG_DATA

