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

from .models import UserSyncAPI
from .schemas import (
    UserSyncAPICreate, 
    UserSyncAPIUpdate,
)
from src.account.cost.controllers import account_cost_controller, AccountCostCreate, CostType

from ..base.models import SyncAPI
from ..base.controllers import sync_api_controller

from ..call.controllers import sync_api_call_controller, SyncAPICallCreate
from ..enums import SyncAPIStatus

class UserSyncAPIController(CRUDBase[UserSyncAPI, UserSyncAPICreate, UserSyncAPIUpdate]):
    def __init__(self):
        super().__init__(model=UserSyncAPI)

    
    async def call(self, user_sync_api: UserSyncAPI, request: Request) -> Tuple[str, str]:
        user : User = await user_sync_api.user
        sync_api : SyncAPI = await user_sync_api.sync_api
        main_key = "_".join([f'{request.query_params.get(k,"")}' for k in sync_api.main_params])
        t = time.time()
        flag, body = await sync_api_controller.call(sync_api, request, user_sync_api.timeout)
        ## 根据body判断是否需要扣费
        if flag == SyncAPIStatus.SUCCESS:
            await account_cost_controller.create(AccountCostCreate(
                user_id=user.id,
                item=sync_api.name,
                amount=user_sync_api.unit_price,
                cost_type=CostType.DEBIT,
                remark=f"同步API {sync_api.name} 调用"
            ))
        await sync_api_call_controller.create(SyncAPICallCreate(
            user_id=user.id,
            sync_api_name=sync_api.name,
            call_time=round(time.time() - t, 3),
            response_size=len(body),
            status=flag,
            main_key=main_key,
        ))
        return flag, body


user_sync_api_controller = UserSyncAPIController()

if __name__ == "__main__":
    pass