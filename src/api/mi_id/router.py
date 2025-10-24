import uuid
import re
import json
from datetime import datetime
from typing import Dict, Any
from fastapi import APIRouter, Query, HTTPException, Body
from fastapi.responses import PlainTextResponse
from pydantic import BaseModel

from src.loger import logger

from .service import MiIdService, APIInfo
service = MiIdService()

router = APIRouter()
@router.post("/", summary="获取mi_id item_url",response_class=PlainTextResponse)
async def current(
    params: APIInfo.Params = Body(..., description="参数"),
):
    mi_id = await service.get_mi_id(params)
    return mi_id

class AddParams(BaseModel):
    item_id: str
    flag : str

@router.post("/flag", summary="添加item_id flag到缓存",response_class=PlainTextResponse)
async def add_flag(
    params: AddParams = Body(..., description="参数"),
):
    return service.redis.hset(service.mi_id_key+":flag", params.item_id, params.flag)

@router.get("/flag", summary="获取item_id flag",response_class=PlainTextResponse)
async def get_flag(
    item_id: str,
):
    return service.redis.hget(service.mi_id_key+":flag", item_id)