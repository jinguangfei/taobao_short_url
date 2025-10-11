import asyncio
import re

from typing import Any, Dict, Generic, List, NewType, Tuple, Type, TypeVar, Union
from fastapi.exceptions import HTTPException
from tortoise.transactions import in_transaction

from src.admin.models import User
from src.core.crud import CRUDBase
from src.account.info.controllers import account_info_controller

from .models import AccountCost, CostType
from .schemas import AccountCostCreate, AccountCostUpdate

class AccountCostController(CRUDBase[AccountCost, AccountCostCreate, AccountCostUpdate]):
    def __init__(self):
        super().__init__(model=AccountCost)

    async def create(self, obj_in: AccountCostCreate) -> AccountCost:
        user = await User.get(id=obj_in.user_id)
        cost = None
        async with in_transaction() as connection:
            # 创建 Cost 记录
            obj_dict = obj_in.model_dump()
            obj_dict["user"] = user
            cost = await self.model.create(**obj_dict, using_db=connection)

            # 根据 Cost 类型更新 Account
            account_info = await account_info_controller.get_by_user(user)
            if obj_in.cost_type == CostType.DEBIT: # 1 为支出
                account_info.balance -= obj_in.amount
            else: # 0 为收入
                account_info.balance += obj_in.amount
            account_info.balance = round(account_info.balance, 3)

            await account_info.save(using_db=connection)

        return cost

account_cost_controller = AccountCostController()

if __name__ == "__main__":
    pass