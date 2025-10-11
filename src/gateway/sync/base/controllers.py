import asyncio
import re
import json
import time
from typing import Optional, Dict, Any, List
import httpx


from typing import Any, Dict, Generic, List, NewType, Tuple, Type, TypeVar, Union
from fastapi import HTTPException, Request

from src.core.crud import CRUDBase
from src.admin.models import User

from .models import SyncAPI
from .schemas import (
    SyncAPICreate, 
    SyncAPIUpdate, 
)
from ..enums import SyncAPIStatus

class SyncAPIController(CRUDBase[SyncAPI, SyncAPICreate, SyncAPIUpdate]):
    def __init__(self):
        super().__init__(model=SyncAPI)

    async def get_by_name(self, name: str) -> SyncAPI:
        return await self.model.filter(name=name).first()

    def build_url(self, sync_api: SyncAPI, query_params: Dict[str, Any]) -> str:
        if sync_api.host.startswith("http"):
            url = sync_api.host
        else:
            url = "http://" + sync_api.host
        if sync_api.path.startswith("/"):
            url = url + sync_api.path
        else:
            url = url + "/" + sync_api.path
        if not sync_api.path.endswith("/"):
            url = url + "/"
        if query_params:
            url = url + "?" + "&".join([f"{k}={v}" for k, v in query_params.items()])
        return url

    async def _call(self, sync_api: SyncAPI, query_params: Dict[str, Any], headers: Dict[str, Any]={}, data: Optional[str] = None, timeout: int = 10) -> str:
        url = self.build_url(sync_api, query_params)
        body = ""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.request(sync_api.method, url, headers=headers, data=data, timeout=timeout)
                body = response.text
        except Exception as e:
            pass
            body = "request failure"
        return body
        
    async def call(self, sync_api: SyncAPI, request: Request, timeout: int = 10) -> Tuple[SyncAPIStatus, str]:
        # 获取所有查询参数
        query_params = request.query_params
        # 过滤允许的查询参数
        allowed_params = {k: v for k, v in query_params.items() if k in sync_api.allow_query_params}
        # 过滤允许的请求头
        allowed_headers = {k: v for k, v in request.headers.items() if k in sync_api.allow_headers}
        data = query_params.get("data", None)
        if data:
            data = json.loads(data)
        body = await self._call(sync_api, allowed_params, allowed_headers, data, timeout)
        flag = self.handle_white_list(sync_api, body)
        return flag, body
    
    def handle_white_list(self, sync_api: SyncAPI, body: str) -> SyncAPIStatus:
        flag = SyncAPIStatus.SUCCESS
        if sync_api.white_list:
            for white_str in sync_api.white_list:
                if white_str in body:
                    flag = SyncAPIStatus.SUCCESS
                    break
            else:
                flag = SyncAPIStatus.FAIL
        print(flag)
        return flag

sync_api_controller = SyncAPIController()

if __name__ == "__main__":
    pass