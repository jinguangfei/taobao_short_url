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
from .service import ShortUrlService
service = ShortUrlService()

CONST_KEY = "short_url"

router = APIRouter()
@router.post("/", summary="获取短链接",response_class=PlainTextResponse)
async def current(
    params: APIInfo.Params = Body(..., description="参数"),
):
    if redis_pool.hexists(CONST_KEY, params.uniq_id):
        flag = "success"
        result = json.loads(redis_pool.hget(CONST_KEY, params.uniq_id))
        logger.info(f"short_url {params.uniq_id} is exists")
    else:
        body = await service.crawl(params)
        flag, result = service.check_body(params, body)
        if flag == "success":
            redis_pool.hset(CONST_KEY, params.uniq_id, result.model_dump_json())
            result = result.model_dump()
    logger.info(f"crawl short_url {params.uniq_id} {flag}")
    return json.dumps({"flag":flag,"result":result},ensure_ascii=False)