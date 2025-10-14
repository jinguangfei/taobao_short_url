import json
from datetime import datetime
from typing import Dict, Any
from fastapi import APIRouter, Query, HTTPException, Body
from fastapi.responses import PlainTextResponse
from pydantic import BaseModel

from src.core.redis_script import redis_pool
from src.loger import logger

from .config import APIInfo
from .service import ShortUrlService
service = ShortUrlService()

CONST_KEY = "short_url"

router = APIRouter()
@router.post("/", summary="获取短链接",response_class=PlainTextResponse)
async def current(
    params: APIInfo.Params = Body(..., description="参数"),
):
    flag, result = await service.get_short_url(params)
    logger.info(f"crawl short_url {params.uniq_id} {flag}")
    return json.dumps({"flag":flag,"result":result},ensure_ascii=False)