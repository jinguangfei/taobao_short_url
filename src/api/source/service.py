import asyncio
import re
import time

from typing import Any, Dict, Generic, List, NewType, Tuple, Type, TypeVar, Union

from tortoise.transactions import in_transaction
from src.core.crud import CRUDBase

from .models import Source
from .schemas import SourceCreate, SourceUpdate

class SourceController(CRUDBase[Source, SourceCreate, SourceUpdate]):
    def __init__(self):
        super().__init__(model=Source)

    async def get_available_resource(self, name: str, add_t: int = 6, expire_time: int = 60*60*24) -> Source:
        """
        纯数据库实现
        """
        cur_t = int(time.time())
        
        # 1. 查找并锁定可用资源
        async with in_transaction() as conn:
            resource = await Source.filter(
                name=name,
                use_t__lt=cur_t,
                init_t__gt=cur_t - expire_time,
                status=1,
            ).select_for_update().first()
            
            if resource:
                # 3. 更新使用时间
                resource.use_t = cur_t + add_t
                await resource.save()
                return resource
        
        return None


source_controller = SourceController()

if __name__ == "__main__":
    pass