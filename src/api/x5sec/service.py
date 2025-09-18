import json
import requests
from typing import Dict, Any, Tuple
import traceback
from src.loger import logger

def get_x5sec(slide_url : str, ua : str, cookie : Dict[str,Any], proxies : Dict[str,str]={}, body : str="", **kwargs) -> str:
    x5sec = ""
    for i in range(4):
        try:
            data = {"url":slide_url,"ua":ua,"cookie":cookie,"proxies":proxies,"body":body}
            api_url = "http://123.56.44.124:9478/ali227"
            res = requests.post(api_url, data=json.dumps(data), timeout=12, headers={'Content-Type': 'application/json'})
            recv_dict : Dict = json.loads(res.text)
            if recv_dict.get("code")==0:
                x5sec = recv_dict.get("x5sec") if recv_dict.get("x5sec") else ""
                break
        except Exception as e:
            logger.error(traceback.format_exc())
            pass
    logger.info(f"get_x5sec {i} {'success' if x5sec else 'failed'}")
    return x5sec
