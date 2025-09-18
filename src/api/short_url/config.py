import time
from typing import List, Dict, ClassVar
from pydantic import BaseModel 
from .enums import ShortTargetUrlType

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
        targetUrlType : ShortTargetUrlType
        cookie : str = ""
        proxies : Dict = {}

        target_url_dict : ClassVar[Dict[ShortTargetUrlType, str]]= {
            ShortTargetUrlType.TAOBAO: "https://item.taobao.com/item.htm?id={item_id}",
            ShortTargetUrlType.LT_TAOBAO: "https://main.m.taobao.com/app/ltao-fe/we-detail/home.html?id={item_id}",
            ShortTargetUrlType.M_TAOBAO: "https://pages-g.m.taobao.com/wow/z/app/detail-next/item/index?x-ssr=true&id={item_id}",
        }

        @property
        def uniq_id(self) -> str:
            return f"{self.targetId}____{self.targetUrlType}"
        
        @property
        def targetUrl(self) -> str:
            return self.target_url_dict[self.targetUrlType].format(item_id=self.targetId)

    headers = api_headers
    url = "https://acs.m.taobao.com/h5/mtop.taobao.sharepassword.generateshorturlnew/1.0/?jsv=2.6.1&appKey=21783927&t=1758168414364&sign=d44c4e2df2f21e38b6bcaaf4f77cc768&api=mtop.taobao.sharepassword.generateshorturlnew&v=1.0&isSec=0&ecode=0&timeout=10000&AntiFlood=true&AntiCreep=true&dataType=json&valueType=string&preventFallback=true&type=json&data=%7B%22bizCode%22%3A%221%22%2C%22extendInfo%22%3A%22%7B%5C%22targetId%5C%22%3A%5C%22834550783063%5C%22%7D%22%2C%22targetUrl%22%3A%22https%3A//main.m.taobao.com/app/ltao-fe/we-detail/home.html%3Fid%3D834550783063%22%7D"
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