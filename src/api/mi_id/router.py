import json
from datetime import datetime
from typing import Dict, Any
from fastapi import APIRouter, Query, HTTPException, Body
from fastapi.responses import PlainTextResponse
from pydantic import BaseModel

from src.core.ctx import CTX_USER_ID, CTX_Q
from src.core.bgtask import BgTasks
from src.core.redis_script import redis_pool
from src.loger import logger

from .config import APIInfo
from .service import MiIdService
service = MiIdService()

CONST_KEY = "mi_id"

router = APIRouter()
@router.post("/", summary="获取mi_id",response_class=PlainTextResponse)
async def current(
    params: APIInfo.Params = Body(..., description="参数"),
):
    body = await service.crawl(params)
    flag, result = service.check_body(params, body)
    logger.info(f"crawl mi_id {flag} {result}")
    return json.dumps({"flag":flag,"result":result},ensure_ascii=False)