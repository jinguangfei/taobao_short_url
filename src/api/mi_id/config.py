import time
from typing import List, Dict, ClassVar, Optional
from pydantic import BaseModel 

class APIInfo(object):

    class Params(BaseModel):
        cookie : Optional[str] = ""
        proxies : Optional[Dict] = {}
        real_time : Optional[bool] = False

    url = "https://h5api.m.taobao.com/h5/mtop.relationrecommend.wirelessrecommend.recommend/2.0/?jsv=2.7.2&appKey=12574478&t=1760178443877&sign=135c013262a656288c1983933f52ae69&v=2.0&timeout=3000&dataType=jsonp&valueType=original&jsonpIncPrefix=pcrecommend&ttid=1%40tbwang_mac_1.0.0%23pc&api=mtop.relationrecommend.WirelessRecommend.recommend&type=originaljsonp&callback=mtopjsonppcrecommend20&data=%7B%22appId%22%3A%2230986%22%2C%22params%22%3A%22%7B%5C%22pageNum%5C%22%3A0%2C%5C%22pageSize%5C%22%3A25%2C%5C%22frontAbId%5C%22%3A%5C%22427503%5C%22%2C%5C%22isFirstPage%5C%22%3Atrue%2C%5C%22myCna%5C%22%3A%5C%22%5C%22%7D%22%7D"