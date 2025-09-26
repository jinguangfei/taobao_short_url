import json
import asyncio
import re

from typing import Any, Dict, Generic, List, NewType, Tuple, Type, TypeVar, Union
from fastapi.exceptions import HTTPException
from tortoise.transactions import in_transaction
from tortoise import Tortoise
from tortoise.expressions import Q

from src.core.crud import CRUDBase
from src.settings import settings

from .models import TbCookie
from .schemas import TbCookieCreate, TbCookieUpdate
from src.core.redis_script import redis_pool, loop_r

class TbCookieController(CRUDBase[TbCookie, TbCookieCreate, TbCookieUpdate]):
    def __init__(self):
        super().__init__(model=TbCookie)
        self.redis = redis_pool

    async def init_view(self,view_name : str,  search : Q = Q()):
        total, list = await self.list(page=1, page_size=10, search=search)

    async def view_get(self, view_name : str, add_t : int = 20):
        one_key, one_key_t, next_t = loop_r(view_name, add_t)
        if one_key:
            return await self.get(one_key)
        else:
            return None







if __name__ == "__main__":
    from src.core.init_app import init_data
    async def main():
        # 初始化数据库
        await init_data()
        
        try:
            # 创建控制器实例并测试
            tb_cookie_controller = TbCookieController()
            result = await tb_cookie_controller.create(TbCookieCreate(cookie="test", unb="test"))
            total, list = await tb_cookie_controller.list(page=1, page_size=10)
            print(f"列表: {await list[0].to_dict()}")
            print(f"总数: {total}")
        finally:
            await Tortoise.close_connections()
            pass
    
    asyncio.run(main())