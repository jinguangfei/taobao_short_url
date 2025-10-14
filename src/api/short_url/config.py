import time
from typing import List, Dict, ClassVar, Optional
from pydantic import BaseModel 
import random
from .enums import ShortTargetUrlType

main_query_fields = ["ttid"]

class APIInfo(object):

    class Params(BaseModel):
        targetId : str
        targetUrlType : ShortTargetUrlType
        cookie : str = ""
        proxies : Optional[Dict] = {}
        mi_id : Optional[str] = ""
        refresh : Optional[bool] = False

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
            if self.mi_id:
                #return self.target_url_dict[self.targetUrlType].format(item_id=self.targetId) + f"&mi_id={self.mi_id}&spm=a215i.730{random.randint(1000,9999)}.a215i.1.712{random.randint(1000,9999)}8VcU4WQ"
                return self.target_url_dict[self.targetUrlType].format(item_id=self.targetId) + f"&mi_id={self.mi_id}&&xxc=ad_ct&skuId=0"
            else:
                return self.target_url_dict[self.targetUrlType].format(item_id=self.targetId)

    url = "https://acs.m.taobao.com/h5/mtop.taobao.sharepassword.generateshorturlnew/1.0/?jsv=2.6.1&appKey=21783927&t=1758168414364&sign=d44c4e2df2f21e38b6bcaaf4f77cc768&api=mtop.taobao.sharepassword.generateshorturlnew&v=1.0&isSec=0&ecode=0&timeout=10000&AntiFlood=true&AntiCreep=true&dataType=json&valueType=string&preventFallback=true&type=json&data=%7B%22bizCode%22%3A%221%22%2C%22extendInfo%22%3A%22%7B%5C%22targetId%5C%22%3A%5C%22834550783063%5C%22%7D%22%2C%22targetUrl%22%3A%22https%3A//main.m.taobao.com/app/ltao-fe/we-detail/home.html%3Fid%3D834550783063%22%7D"

    class ShortInfo(BaseModel):
        short_url : str
        long_url : str
        item_id : str
        target_url : str
        unb : str
        t : str