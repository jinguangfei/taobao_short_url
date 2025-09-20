import json
import requests
from typing import Dict, Any, Tuple
import traceback
from src.loger import logger
from .config import APIInfo

def parse_cookie_str(cookie_str : str) -> Dict[str,Any]:
    cookie_dict = {i.split("=")[0]:i.split("=",1)[1] for i in cookie_str.replace("; ",";").split(";") if len(i.split("="))>1}
    return cookie_dict

def get_x5sec(slide_url : str, ua : str, cookie_dict : Dict[str,Any], proxies : Dict[str,str]={}, body : str="", **kwargs) -> str:
    x5sec = ""
    for i in range(kwargs.get("max_times", 4)):
        try:
            data = {"url":slide_url,"ua":ua,"cookie":cookie_dict,"proxies":proxies,"body":body}
            res = requests.post(
                APIInfo.url, 
                data=json.dumps(data), 
                timeout=APIInfo.timeout, 
                headers=APIInfo.headers
                )
            recv_dict : Dict = json.loads(res.text)
            logger.info(f"get_x5sec {i} {slide_url} {recv_dict}")
            if recv_dict.get("code")==0:
                x5sec = recv_dict.get("x5sec") if recv_dict.get("x5sec") else ""
                break
        except Exception as e:
            logger.error(traceback.format_exc())
            pass
    logger.info(f"get_x5sec {i} {'success' if x5sec else 'failed'}")
    return x5sec

if __name__ == "__main__":
    slide_url = "https://ipassport.damai.cn:443//newlogin/login.do/_____tmd_____/punish?x5secdata=xg8ae40414c226e986ja6cf36cfd78db05e5ac1f41ec8c69a27d1758345871a-717315356a1800292054abaac3dakcapslidev233bde8b87fd002310a29bdced656c522b1e__bx__ipassport.damai.cn:443/newlogin/login.do&x5step=2&action=captchacapslidev2&pureCaptcha="
    print(get_x5sec(slide_url,APIInfo.ua,{},{},""))