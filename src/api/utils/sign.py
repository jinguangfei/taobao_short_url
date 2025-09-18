import time
import hashlib
import json
from typing import Dict, Any, Tuple

def md5_data(tk: str, data_str : str = "", t : str = "", app_key : str = "12574478") -> Tuple[str,str]:
    t = t if t else str(int(time.time()*1000))
    app_key = app_key if app_key else "12574478"
    data = (r'%s&%s&%s&%s' % (tk,t,app_key,data_str)).encode("utf-8")
    m = hashlib.md5()
    m.update(data)
    sign = m.hexdigest()
    return t, sign, data_str