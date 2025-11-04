import urllib
import asyncio
import re
import time
import json
import requests
import traceback
import httpx
from typing import Dict, Union

from urllib.parse import urlparse, parse_qs
import uuid

from .config import APIInfo
from src.core.redis_script import redis_pool,zpop_min
from src.loger import logger
from ..base.service import BaseService, APIInfo as BaseAPIInfo
from src.api.utils.taobao_req import parse_url


class MiIdService(BaseService):
    def __init__(self):
        self.redis = redis_pool
        self.mi_id_key = "source:mi_id:haier_sale"

    @staticmethod
    def parse_miid(url: str) -> Union[str, None]:
        """从URL中解析并提取mi_id参数
        
        Args:
            url: 包含查询参数的URL字符串
            
        Returns:
            mi_id值，如果不存在则返回None
        """
        query_params = parse_qs(urlparse(url).query)
        mi_id = query_params.get("mi_id", [None])[0]
        return mi_id

    async def crawl(self, params: APIInfo.Params) -> str:
        url = APIInfo.url
        uuid1 = str(uuid.uuid4())
        uuid2 = str(uuid.uuid4())
        data = {
            "url":f"https://huodong.taobao.com/wow/a/act/tao/dailygroup/23509/24308/wupr?spm=a21bo.jianhua/a.yingxiao.d1_1.5af92a89QItWJ9&wh_pid=daily-561441&itemId={params.item_id}",
            "cookie":"hng=CN|zh-CN|CNY|156",
            "device":"pc",
            "backupParams":"excludes,device",
            "usePrefetch":False,
            "fri":"{\"dtcFloor\":[\"3560263560\",\"5157282990\",\"3186795390\"],\"moduleIdList\":[\"4023243930\",\"8583094810\",\"3215547140\",\"7533668550\",\"5278262170\",\"8399974670\",\"7215635030\",\"4523601760\",\"8684301500\",\"5858859060\",\"1768544000\",\"4627068960\"],\"processedTppId\":[]}",
            "excludes":"3215547140;4023243930;5278262170;7215635030;7533668550;8399974670;8583094810",
            "pvuuid":f"v1-{uuid1}-{int(time.time()*1000)}",
            "schemaVersion":uuid2,
            "sequence":2}

        crawl_params = BaseAPIInfo.Params(url=url, data=data, proxies=params.proxies)
        body = await self._crawl(crawl_params)
        return body

    async def crawl_mi_id(self, params: APIInfo.Params) -> str:
        body = await self.crawl(params)
        self.check_body(body)

    async def get_mi_id(self, params: APIInfo.Params) -> str:
        item_url = self.redis.hget(self.mi_id_key, params.item_id)
        if item_url:
            pass
        else:
            await self.crawl_mi_id(params)
            item_url = self.redis.hget(self.mi_id_key, params.item_id)
        item_url = item_url.decode("utf-8") if isinstance(item_url, bytes) else item_url
        item_url = self.parse_mi_id(item_url)
        return item_url

    def parse_mi_id(self, mi_id: str) -> str:
        if mi_id and mi_id.find("utparam=null") > -1:
            url, query_params = parse_url(mi_id)
            item_id = query_params.get("id")
            scm = query_params.get("scm")
            pvid = str(uuid.uuid4())
            utparam = '{"floorId":42001303,"recIndex":5,"x_object_type":"item","pvid":"%s","x_item_ids":%s,"scm":"%s","x_object_id":%s,"tpp_buckets":"302#0#273555#0_30636#0#273555#0"}' % (pvid,item_id,scm,item_id)
            query_params["utparam"] = utparam
            mi_id = url + "?" + urllib.parse.urlencode(query_params)
        return mi_id.replace("://","") if mi_id else ""

    def _check_body(self, body: str) -> Dict[str, str]:
        item_url_list = re.findall(r'itemUrl":"//(.*?)"',body)
        item_id_dict = {}
        for item_url in item_url_list:
            id_g = re.search(r'(\?|&)id=(\d+)',item_url)
            item_id = id_g.group(2) if id_g else ""
            if item_id and item_url.find("mi_id")>-1:
                #mi_id = self.parse_miid(item_url)
                item_id_dict[item_id] = item_url
        return item_id_dict
    
    def check_body(self, body: str) -> Dict[str, str]:
        recv_dict = self._check_body(body)
        if recv_dict:
            self.redis.hmset(self.mi_id_key, mapping=recv_dict)
        return recv_dict

    def chouqu_mi_id(self, file_name: str) -> Dict[str, str]:
        with open(file_name, "r") as f:
            item_miid_list = f.readlines()
            item_miid_list = [line.strip() for line in item_miid_list if line.strip()]
            item_miid_dict = {}
            for i in item_miid_list:
                parts = i.split()
                if len(parts) >= 2:
                    item_id = parts[0]
                    url = parts[1]
                    item_miid_dict[item_id] = url
        self.redis.hmset(self.mi_id_key, mapping=item_miid_dict)



if __name__ == "__main__":
    service = MiIdService()
    params = APIInfo.Params(item_id="593147834457",proxies={})
    #body = asyncio.run(service.crawl_mi_id(params))
    service.chouqu_mi_id("20251030_xmz2_sale")
    print(service.redis.hlen(service.mi_id_key))
    #print(asyncio.run(service.get_mi_id(params)))