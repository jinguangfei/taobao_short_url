import time
from typing import List, Dict, ClassVar, Optional
from pydantic import BaseModel 

main_query_fields = ["ttid"]

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



class APIInfo(object):

    class Params(BaseModel):
        targetId : str
        cookie : str = ""
        proxies : Optional[Dict] = {}

        @property
        def uniq_id(self) -> str:
            return f"{self.targetId}____{self.targetUrlType}"

    headers = api_headers
    collect_url = "https://h5api.m.tmall.com/h5/mtop.taobao.mercury.addcollect/1.0/?jsv=2.7.4&appKey=12574478&t=1760387152673&sign=c2c39607373f15c935286d4860ecfe9a&api=mtop.taobao.mercury.addCollect&v=1.0&isSec=0&ecode=0&timeout=10000&dataType=json&valueType=string&needEcodeSign=true&LoginRequest=true&needLogin=true&bizName=msoa.taobao.check.collect.h5&sceneName=main_check_collect_h5&type=json&data=%7B%22itemId%22%3A%22744189867030%22%2C%22type%22%3A%221%22%2C%22appName%22%3A%22detailH5%22%7D"
    item_list_url = "https://h5api.m.taobao.com/h5/mtop.taobao.mercury.platform.collections.get/5.1/?jsv=2.7.2&appKey=12574478&t=1760387765317&sign=e7eba8dff129dca382733c108e5b4cdb&api=mtop.taobao.mercury.platform.collections.get&v=5.1&timeout=10000&jsonpIncPrefix=mytbpc&preventFallback=true&type=jsonp&dataType=jsonp&callback=mtopjsonpmytbpc7&data=%7B%22itemType%22%3A1%2C%22platformCode%22%3A0%2C%22appName%22%3A%22favorite%22%2C%22pageSize%22%3A50%2C%22pageNum%22%3A0%2C%22startTime%22%3A%220%22%2C%22weexVersion%22%3A2%7D"
    level = 100
    flag_score = {"slide":2,"deny":3,"deny2":3,"login":4,"success":1,"xiajia":1,"noitem":1}
    add_time = 8
    max_use_times = 1570
    max_use_sleep_time = 60 * 60 * 24
    slide_time = 60 
    deny_time = 60 * 30
    login_time = 60*60*24*7
