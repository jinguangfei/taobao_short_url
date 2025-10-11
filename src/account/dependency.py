from typing import Optional
from fastapi import FastAPI, Depends, Query, Header, HTTPException, Request
from tortoise.expressions import Q

from src.core.ctx import CTX_TOKEN, CTX_Q, CTX_USER_ID

from src.core.dependency import AuthControl, User

from .info.models import AccountInfo

class AccountTokenControl:
    @classmethod
    async def validate_token(cls, token: str = Query(..., description="token验证")) -> None:
        try:
            account_info : Optional[AccountInfo] = await AccountInfo.filter(token=token).first()
            if not account_info:
                raise HTTPException(status_code=401, detail="Token 不存在")
            if not account_info.is_active:
                raise HTTPException(status_code=401, detail="Token 已失效")
            return account_info
        except Exception as e:
            raise HTTPException(status_code=403, detail=f"{repr(e)}")