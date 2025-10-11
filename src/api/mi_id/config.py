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
        cookie : Optional[str] = ""
        proxies : Optional[Dict] = {}

    headers = api_headers
    url = "https://h5api.m.taobao.com/h5/mtop.relationrecommend.wirelessrecommend.recommend/2.0/?jsv=2.7.2&appKey=12574478&t=1760178443877&sign=135c013262a656288c1983933f52ae69&v=2.0&timeout=3000&dataType=jsonp&valueType=original&jsonpIncPrefix=pcrecommend&ttid=1%40tbwang_mac_1.0.0%23pc&api=mtop.relationrecommend.WirelessRecommend.recommend&type=originaljsonp&callback=mtopjsonppcrecommend20&data=%7B%22appId%22%3A%2230986%22%2C%22params%22%3A%22%7B%5C%22pageNum%5C%22%3A0%2C%5C%22pageSize%5C%22%3A25%2C%5C%22frontAbId%5C%22%3A%5C%22427503%5C%22%2C%5C%22isFirstPage%5C%22%3Atrue%2C%5C%22myCna%5C%22%3A%5C%22%5C%22%7D%22%7D"
    level = 100
    flag_score = {"slide":2,"deny":3,"deny2":3,"login":4,"success":1,"xiajia":1,"noitem":1}
    add_time = 8
    max_use_times = 1570
    max_use_sleep_time = 60 * 60 * 24
    slide_time = 60 
    deny_time = 60 * 30
    login_time = 60*60*24*7
