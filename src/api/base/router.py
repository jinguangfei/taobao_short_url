import json
from datetime import datetime
from typing import Dict, Any
from fastapi import APIRouter, Query, HTTPException, Body
from fastapi.responses import PlainTextResponse

from .service import BaseService, APIInfo
service = BaseService()

router = APIRouter()
@router.post("/", summary="base_crawl",response_class=PlainTextResponse)
async def current(
    params: APIInfo.Params = Body(..., description="参数"),
):
    return await service._crawl(params)