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
@router.post("/", summary="获取mi_id",response_class=PlainTextResponse)
async def current(
    params: APIInfo.Params = Body(..., description="参数"),
):
    mi_id = await service.get_mi_id(params)
    logger.info(f"crawl mi_id {mi_id}")
    return json.dumps({"flag":"success","result":mi_id},ensure_ascii=False)