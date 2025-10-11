from fastapi import FastAPI, Depends, Query, Header, HTTPException, Request

from src.account.dependency import AccountTokenControl, AccountInfo
from src.gateway.sync.base.controllers import sync_api_controller
from src.gateway.sync.user.controllers import user_sync_api_controller
from src.core.redis_script import choke_func
from src.settings.config import settings

class SyncTokenControl:

    @classmethod
    async def validate_token(cls, api_name : str , account_info: AccountInfo= Depends(AccountTokenControl.validate_token)) -> UserSyncGateway:
        limit_key = f"{account_info.token}:{api_name}"
        user = await account_info.user
        # 获取同步网关
        sync_api = await sync_api_controller.get_by_name(api_name)
        if sync_api is None:
            raise HTTPException(status_code=201, detail="API 不存在")
        # 获取用户同步网关
        user_sync_api = await user_sync_api_controller.model.filter(user=user, sync_api=sync_api).first()
        # 如果用户同步网关不存在,则抛出异常
        if user_sync_api is None:
            raise HTTPException(status_code=201, detail="没有订阅")
        # 如果用户余额不足,则抛出异常
        if account_info.balance < user_sync_api.unit_price:
            raise HTTPException(status_code=201, detail="余额不足")
        # 限制API调用速率
        if not choke_func(
            handler_key=settings.REDIS_API_TOKEN_LIMIT_KEY, 
            token=limit_key,
            capacity=user_sync_api.capacity,
            rate=user_sync_api.rate,
        ):
            raise HTTPException(status_code=201, detail="API 调用次数过快")
        return user_sync_api

DependSyncToken = Depends(SyncTokenControl.validate_token)