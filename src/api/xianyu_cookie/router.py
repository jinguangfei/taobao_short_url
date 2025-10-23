import json
from datetime import datetime
from typing import Dict, Any, Literal
from fastapi import APIRouter, Query, HTTPException, Body, Path
from fastapi.responses import PlainTextResponse
from pydantic import BaseModel

from src.core.schemas import Success, Fail
from src.loger import logger

from .service import XianyuReloginService, APIInfo
service = XianyuReloginService()

router = APIRouter()
@router.post("/relogin", summary="闲鱼重新登录",response_class=PlainTextResponse)
async def relogin(
    params: APIInfo.Params = Body(..., description="参数"),
):
    flag, cookies = await service.get_new_cookies(params.cookie_str, proxies=params.proxies)
    return Success(
        data={
            "flag":flag.value,
        }
    )
