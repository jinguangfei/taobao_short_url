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

from .models import UserExtFunction
from .schemas import (
    UserExtFunctionCreate, 
    UserExtFunctionUpdate,
)
from ..enums import ExtFunctionStatus
from src.account.cost.controllers import account_cost_controller, AccountCostCreate, CostType

from ..base.models import ExtFunction

from ..call.controllers import ext_function_call_controller, ExtFunctionCallCreate

class UserExtFunctionController(CRUDBase[UserExtFunction, UserExtFunctionCreate, UserExtFunctionUpdate]):
    def __init__(self):
        super().__init__(model=UserExtFunction)

    async def get_by_name(self, user_id: int, name: str) -> UserExtFunction:
        return await self.model.get_or_none(user_id=user_id, ext_function__name=name)

    async def over(self, user_ext_function: UserExtFunction, main_key : str, flag : bool, body : str, call_time : float) -> Any:
        user : User = await user_ext_function.user
        ext_function : ExtFunction = await user_ext_function.ext_function
        if flag:
            await account_cost_controller.create(AccountCostCreate(
                user_id=user.id,
                item=ext_function.name,
                amount=user_ext_function.unit_price,
                cost_type=CostType.CREDIT,
                remark=f"插件功能 {ext_function.name} 调用"
            ))
        await ext_function_call_controller.create(ExtFunctionCallCreate(
            user_id=user.id,
            ext_function_name=ext_function.name,
            call_time=call_time,
            response_size=len(body),
            status=ExtFunctionStatus.SUCCESS if flag in {True, "success", "noitem"} else ExtFunctionStatus.FAIL,
            main_key=main_key,
        ))
    
user_ext_function_controller = UserExtFunctionController()

if __name__ == "__main__":
    pass